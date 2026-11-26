#!/usr/bin/env python3
"""Generates Box.asm for your K.  Usage: python make_box.py 41"""
import sys
K = int(sys.argv[1])
ROWS = 20
WORDS = (K % 4) + 1                 # width = 16 * WORDS pixels
START = 16384 + 32 * K              # SCREEN + 32*K

asm = f"""// Box.asm  -  K = {K}
// Box starts at row {K}, {ROWS} rows tall, {16*WORDS} pixels wide ({WORDS} word(s)).
// Key pressed -> black box, key released -> box cleared.

(MAIN)
    @KBD
    D=M
    @BLACK
    D;JNE           // key pressed?
    @color
    M=0             // white
    @DRAW
    0;JMP
(BLACK)
    @color
    M=-1            // black (all 16 bits set)

(DRAW)
    @{START}
    D=A
    @addr           // address of first word of current row
    M=D
    @{ROWS}
    D=A
    @rows
    M=D

(ROWLOOP)
    @{WORDS}
    D=A
    @cols
    M=D
    @addr
    D=M
    @p              // p = pointer to current word
    M=D

(COLLOOP)
    @color
    D=M
    @p
    A=M
    M=D             // paint one word (16 pixels)
    @p
    M=M+1
    @cols
    M=M-1
    D=M
    @COLLOOP
    D;JGT

    @32             // next screen row
    D=A
    @addr
    M=D+M
    @rows
    M=M-1
    D=M
    @ROWLOOP
    D;JGT

    @MAIN
    0;JMP
"""
open('Box.asm', 'w').write(asm)
print('Wrote Box.asm for K =', K)
