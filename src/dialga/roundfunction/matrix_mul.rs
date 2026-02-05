use crate::dialga::helper::state::State;

#[deprecated]
pub fn matrix_mul_old(state: &mut State, i: usize) { // make state mutalble for now (i think this is the better way, can check AES impl later
    let pre_mix:State = *state;

    // Wrong!!
    state.0[0][i] = pre_mix.0[1][i] ^ pre_mix.0[2][i] ^ pre_mix.0[3][i];
    state.0[1][i] = pre_mix.0[0][i] ^ pre_mix.0[2][i] ^ pre_mix.0[3][i];
    state.0[2][i] = pre_mix.0[0][i] ^ pre_mix.0[1][i] ^ pre_mix.0[3][i];
    state.0[3][i] = pre_mix.0[0][i] ^ pre_mix.0[1][i] ^ pre_mix.0[2][i];
}

pub fn matrix_mul(state: &mut State) { //Midori shuffles every column of the matrix, maybe they do here too

    /* i-th State column multiplied with Matrix --> self inverse
    * (0 1 1 1)
    * (1 0 1 1)
    * (1 1 0 1)
    * (1 1 1 0)*/

    let pre_mix: [[u8; 4]; 4] = state.0;

    for col in 0..4 {
        state.0[col][0] = pre_mix[col][1] ^ pre_mix[col][2] ^ pre_mix[col][3];
        state.0[col][1] = pre_mix[col][0] ^ pre_mix[col][2] ^ pre_mix[col][3];
        state.0[col][2] = pre_mix[col][0] ^ pre_mix[col][1] ^ pre_mix[col][3];
        state.0[col][3] = pre_mix[col][0] ^ pre_mix[col][1] ^ pre_mix[col][2];
    }
}