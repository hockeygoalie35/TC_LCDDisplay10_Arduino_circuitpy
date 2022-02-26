# Ported to micropy from https://github.com/turing-complete-labs/LCDDisplay10_Arduino

import time

class LCDDisplay10:

    #     AAA
    #    D   C
    #    D   C
    #     FFF
    #    E   B
    #    E   B
    #     GGG  PP

    SEG_A = 0b10000000
    SEG_B = 0b01000000
    SEG_C = 0b00100000
    SEG_D = 0b00001000
    SEG_E = 0b00000100
    SEG_F = 0b00000010
    SEG_G = 0b00000001

    SEG_P = 0b00010000

    DIGIT_SEGMENTS = [
        SEG_A | SEG_C | SEG_B | SEG_G | SEG_E | SEG_D,
        SEG_C | SEG_B,
        SEG_A | SEG_C | SEG_G | SEG_E | SEG_F,
        SEG_A | SEG_C | SEG_B | SEG_G | SEG_F,
        SEG_C | SEG_B | SEG_D | SEG_F,
        SEG_A | SEG_B | SEG_G | SEG_D | SEG_F,
        SEG_A | SEG_B | SEG_G | SEG_E | SEG_D | SEG_F,
        SEG_A | SEG_C | SEG_B,
        SEG_A | SEG_C | SEG_B | SEG_G | SEG_E | SEG_D | SEG_F,
        SEG_A | SEG_C | SEG_B | SEG_G | SEG_D | SEG_F]

    BUFFER_SIZE = 14
    DIGITS = 10
    FLAGS = 12

    SEG_Err = 0b00010000
    SEG_Mem = 0b00100000
    SEG_Min = 0b01000000

    TS_SIZE = 7
    TS_SEGMENTS = [
    0b1000000000000000,
    0b0000100000000000,
    0b0000001000000000,
    0b0000010000000000,
    0b0000000001000000,
    0b0000000000100000,
    0b0000000010000000]

    T_1 = 0b01000000
    T_2 = 0b00100000
    T_3 = 0b00010000
    T_4 = 0b00001000
    T_5 = 0b00000100
    T_6 = 0b00000010
    T_7 = 0b00000001

    TS_INDEX = [T_1, T_2, T_3, T_4, T_5, T_6, T_7];

    DEVICE_ADDR = 0x38

    def __init__(self, i2c):
        self._i2c = i2c
        self._buffer = []

    def fillDigits(self, c):
        for i in range(self.DIGITS):
            self._buffer[i] = c

    def write_to_buffer(self, number: str) -> bool:
        cur_pos = 0
        n_len = 0
        write_buffer = [0] * self.DIGITS

        self.fill(0) # added
        number_as_a_list = list(number)

        is_negative = number_as_a_list[0] == '-'
        if is_negative:
            self.set_negative(is_negative)
            number_as_a_list = number_as_a_list[1:]

        for c in number_as_a_list:
            if n_len >= 10:
                break

            if (c == '.'):
                if not cur_pos:
                    write_buffer[cur_pos] = self.SEG_P
                else:
                    write_buffer[cur_pos - 1] |= self.SEG_P
                continue

            if (c == ' '):
                write_buffer[cur_pos] = 0;
                n_len = n_len + 1
                cur_pos = cur_pos + 1
                continue;

            if ((c >= '0') and (c <= '9')):
                idx = ord(c) - ord('0')
                write_buffer[cur_pos] = self.DIGIT_SEGMENTS[idx]
                n_len = n_len + 1
                cur_pos = cur_pos + 1
                continue
            return False

        self.fillDigits(0)
        self._buffer[0] = 0xe0
        self._buffer[1] = 0
        for i in range(n_len):
            a = 10 - n_len + i
            b = n_len - i - 1
            self._buffer[10 - n_len + i + 2] = write_buffer[n_len - i - 1];

        return True

    def send_command(self, command, val):
        n_ack = self._i2c.writeto(self.DEVICE_ADDR,bytes([command,val]))

    def reset(self) -> None:
        self.send_command(0xe0, 0x48)
        time.sleep_ms(3)
        self.send_command(0xe0, 0x70)

    def print_to_lcd(self, number: str):
        res = self.write_to_buffer(number)
        if (res):
            self.send_buffer();

    def fill(self, c:str):
        self._buffer.clear()
        for i in range(self.BUFFER_SIZE):
            self._buffer.append(c)

    def set_memory(self, memory_flag: bool) -> None:
        if memory_flag:
            self._buffer[self.FLAGS] = self._buffer[self.FLAGS] | self.SEG_Mem
        else:
            self._buffer[self.FLAGS] = self._buffer[self.FLAGS] and not self.SEG_Mem

    def set_negative(self, negative_flag):
        if negative_flag:
            self._buffer[self.FLAGS] = self._buffer[self.FLAGS] | self.SEG_Min
        else:
            self._buffer[self.FLAGS] = self._buffer[self.FLAGS] & ~self.SEG_Min;

    def set_error(self, error_flag):
        if error_flag:
            self._buffer[self.FLAGS] = self._buffer[self.FLAGS] | self.SEG_Err
        else:
            self._buffer[self.FLAGS] = self._buffer[self.FLAGS] & ~self.SEG_Err;

    def set_digit(self, pos, value):
        if pos < self.DIGITS:
            if value >= 0 and value <= 9:
                self._buffer[pos] = self._buffer[pos] & self.SEG_P  | self.DIGIT_SEGMENTS[value]
            else:
                 self._buffer[pos] = 0

    def set_point_pos(self, pos):
        if pos < self.DIGITS:
            for dp in range(2, self.DIGITS):
                self._buffer[dp] =  self._buffer[dp] & ~self.SEG_P;
            self._buffer[pos + 2] |= self.SEG_P

    def set_thousands(self, n):
        on_bits = 0
        off_bits = 0
        for i in range(self.TS_SIZE):
            if self.TS_INDEX[i] & n:
                on_bits |= self.TS_SEGMENTS[i]
            else:
                off_bits != self.TS_SEGMENTS[i]

        off_bits = ~off_bits;
        old_value = self._buffer[self.FLAGS];
        self._buffer[self.FLAGS] = (old_value | (on_bits >> 8)) & (off_bits >> 8);
        old_value = self._buffer[self.FLAGS + 1];
        self._buffer[self.FLAGS + 1] = (old_value | (on_bits & 0xff)) & (off_bits & 0xff);

    def clear(self):
        self.fill(0)
        self.send_buffer()

    def send_buffer(self):
        n_ack = self._i2c.writeto(self.DEVICE_ADDR, bytearray(self._buffer))
