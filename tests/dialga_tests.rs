

#[cfg(test)]
mod tests {
    use dialga_cipher_rust::dialga::*;

    const TEST_STATE: State = State([
            [0xFF, 0x01, 0x02, 0x03],
            [0x10, 0x11, 0x12, 0x13],
            [0x20, 0x21, 0x22, 0x23],
            [0x30, 0x31, 0x32, 0x33],
        ]);

    #[test]
    fn test_matrix_mul() {
        let mut state: State = TEST_STATE;
        
        for i in 0..4 {
            matrix_mul(&mut state, i);
            matrix_mul(&mut state, i);
            assert_eq!(TEST_STATE, state);
        }
    }

    #[test]
    fn test_byte_perm() {
        let mut state = TEST_STATE;

        for i in 0..4 {
            byte_permutation(&mut state, i);
            byte_permutation_inv(&mut state, i);
            assert_eq!(TEST_STATE, state)
        }
    }

    #[test]
    fn test_state_from() {
        let state1 = State::from([0xFF_u8, 0x10, 0x20, 0x30, 0x01, 0x11, 0x21, 0x31, 0x02, 0x12, 0x22, 0x32, 0x03, 0x13, 0x23, 0x33]);
        assert_eq!(TEST_STATE, state1);

        println!("{:?}", state1);
    }
}

