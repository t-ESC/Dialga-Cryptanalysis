use std::convert::From;

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub struct State(pub [[u8; 4];4]);

impl State {
    pub fn new(data: [[u8; 4];4]) {
        State(data);
    }

    pub fn from_flat(data: [u8; 16]) -> State {
        let mut mat = [[0_u8; 4];4];
        for i in 0..16 {
            let j = i % 4;
            let k = i / 4;
            mat[j][k] = data[i]; 
        }
        State(mat)
    }
}

impl From<[u8; 16]> for State {
    fn from(value: [u8; 16]) -> Self {
        State::from_flat(value)
    }
}

pub fn matrix_mul(state: &mut State, i: usize) { // make state mutalble for now (i think this is the better way, can check AES impl later
    
    /* State column multiplied with Matrix --> self inverse
    * (0 1 1 1)
    * (1 0 1 1)
    * (1 1 0 1)
    * (1 1 1 0)*/

    let pre_mix:State = *state;
    
    state.0[0][i] = pre_mix.0[1][i] ^ pre_mix.0[2][i] ^ pre_mix.0[3][i];
    state.0[1][i] = pre_mix.0[0][i] ^ pre_mix.0[2][i] ^ pre_mix.0[3][i];
    state.0[2][i] = pre_mix.0[0][i] ^ pre_mix.0[1][i] ^ pre_mix.0[3][i];
    state.0[3][i] = pre_mix.0[0][i] ^ pre_mix.0[1][i] ^ pre_mix.0[2][i];

}
