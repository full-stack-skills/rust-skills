#[derive(Debug, Eq, PartialEq)]
pub enum TransferError<E> {
    InvalidAmount,
    Store(E),
}

pub trait AccountTransaction {
    type Error;

    fn debit(&mut self, account: usize, amount: i64) -> Result<(), Self::Error>;
    fn credit(&mut self, account: usize, amount: i64) -> Result<(), Self::Error>;
    fn commit(self) -> Result<(), Self::Error>;
}

pub fn transfer<T: AccountTransaction>(
    mut transaction: T,
    from: usize,
    to: usize,
    amount: i64,
) -> Result<(), TransferError<T::Error>> {
    if amount <= 0 {
        return Err(TransferError::InvalidAmount);
    }

    transaction
        .debit(from, amount)
        .map_err(TransferError::Store)?;
    transaction
        .credit(to, amount)
        .map_err(TransferError::Store)?;
    transaction.commit().map_err(TransferError::Store)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[derive(Debug, Eq, PartialEq)]
    enum FakeError {
        InsufficientFunds,
        CreditFailed,
    }

    struct FakeDatabase {
        balances: [i64; 2],
    }

    struct FakeTransaction<'a> {
        database: &'a mut FakeDatabase,
        staged: [i64; 2],
        fail_credit: bool,
    }

    impl FakeDatabase {
        fn begin(&mut self, fail_credit: bool) -> FakeTransaction<'_> {
            FakeTransaction {
                staged: self.balances,
                database: self,
                fail_credit,
            }
        }
    }

    impl AccountTransaction for FakeTransaction<'_> {
        type Error = FakeError;

        fn debit(&mut self, account: usize, amount: i64) -> Result<(), Self::Error> {
            if self.staged[account] < amount {
                return Err(FakeError::InsufficientFunds);
            }
            self.staged[account] -= amount;
            Ok(())
        }

        fn credit(&mut self, account: usize, amount: i64) -> Result<(), Self::Error> {
            if self.fail_credit {
                return Err(FakeError::CreditFailed);
            }
            self.staged[account] += amount;
            Ok(())
        }

        fn commit(self) -> Result<(), Self::Error> {
            self.database.balances = self.staged;
            Ok(())
        }
    }

    #[test]
    fn commits_the_complete_use_case() {
        let mut database = FakeDatabase {
            balances: [100, 20],
        };

        assert_eq!(transfer(database.begin(false), 0, 1, 30), Ok(()));
        assert_eq!(database.balances, [70, 50]);
    }

    #[test]
    fn drops_uncommitted_staged_changes_after_failure() {
        let mut database = FakeDatabase {
            balances: [100, 20],
        };

        assert_eq!(
            transfer(database.begin(true), 0, 1, 30),
            Err(TransferError::Store(FakeError::CreditFailed))
        );
        assert_eq!(database.balances, [100, 20]);
    }
}
