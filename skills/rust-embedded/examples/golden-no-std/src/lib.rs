#![no_std]

pub trait OutputPin {
    type Error;

    fn set_high(&mut self) -> Result<(), Self::Error>;
    fn set_low(&mut self) -> Result<(), Self::Error>;
}

pub fn pulse<P: OutputPin>(pin: &mut P) -> Result<(), P::Error> {
    pin.set_high()?;
    pin.set_low()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[derive(Default)]
    struct FakePin {
        high_calls: usize,
        low_calls: usize,
        fail_low: bool,
    }

    impl OutputPin for FakePin {
        type Error = &'static str;

        fn set_high(&mut self) -> Result<(), Self::Error> {
            self.high_calls += 1;
            Ok(())
        }

        fn set_low(&mut self) -> Result<(), Self::Error> {
            self.low_calls += 1;
            if self.fail_low {
                Err("low transition failed")
            } else {
                Ok(())
            }
        }
    }

    #[test]
    fn exercises_the_portable_driver_on_the_host() {
        let mut pin = FakePin::default();

        assert_eq!(pulse(&mut pin), Ok(()));
        assert_eq!((pin.high_calls, pin.low_calls), (1, 1));
    }

    #[test]
    fn preserves_hal_errors() {
        let mut pin = FakePin {
            fail_low: true,
            ..FakePin::default()
        };

        assert_eq!(pulse(&mut pin), Err("low transition failed"));
    }
}
