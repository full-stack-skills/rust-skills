#[derive(Debug, Eq, PartialEq)]
pub enum AverageError {
    Empty,
    Overflow,
}

pub fn average(values: &[u64]) -> Result<u64, AverageError> {
    if values.is_empty() {
        return Err(AverageError::Empty);
    }
    let sum = values
        .iter()
        .try_fold(0_u64, |total, value| total.checked_add(*value))
        .ok_or(AverageError::Overflow)?;
    Ok(sum / values.len() as u64)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_empty_input() {
        assert_eq!(average(&[]), Err(AverageError::Empty));
    }
}
