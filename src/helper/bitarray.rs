use std::{convert::From};

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub struct BitArray (pub [bool; 8]); // ASSUMPTION: Most Significant Bit First

impl From<u8> for BitArray {
    fn from(value: u8) -> Self {
        let mut output = [false; 8];
        for j in 0..8 {
            if value&(1<<j) > 0 { // First Element here is least significant bit
                output[7-j] = true;
            }
        }
        BitArray(output)
    }
}

impl Into<u8> for BitArray {
    fn into(self) -> u8 {
        let mut output = 0u8;
        for j in 0..8 {
            if self.0[j] {
                output += 1 << (7-j);
            }
        }
        return output;
    }
}