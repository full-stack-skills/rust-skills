/// Read one element through a raw pointer.
///
/// # Safety
///
/// `values` must point to `len` initialized `u32` values for the duration of
/// the call. `index` must be smaller than `len`.
pub unsafe fn read_at(values: *const u32, len: usize, index: usize) -> Option<u32> {
    if values.is_null() || index >= len {
        return None;
    }
    // SAFETY: The caller guarantees a valid allocation and the bounds check
    // above proves that `index` selects an initialized element.
    Some(unsafe { *values.add(index) })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reads_in_bounds() {
        let values = [7, 11];
        // SAFETY: `values` is alive and contains two initialized elements.
        assert_eq!(
            unsafe { read_at(values.as_ptr(), values.len(), 1) },
            Some(11)
        );
    }
}
