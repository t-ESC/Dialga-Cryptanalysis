use dialga_cipher_rust::dialga::*;

#[test]
fn test_matrix_mul() {
    let mut state: State = State([
        [0xFF, 0x01, 0x02, 0x03],
        [0x10, 0x11, 0x12, 0x13],
        [0x20, 0x21, 0x22, 0x23],
        [0x30, 0x31, 0x32, 0x33],
    ]);
    for i in 0..4 {
        let original = state;
        matrix_mul(&mut state, i);
        matrix_mul(&mut state, i);
        assert_eq!(original, state);
    }
}