preload:
    time:   .string "The current time is "
    on:     .string " on "
    invis:  .string "\033[?25l"
    show:   .string "\033[?25h"
    escape: .string "\033["

fix_hour:
    sub r1, r2
    ret

fix_hour_init:
    jgt fix_hour
    ret

zero_pad:
    ldi r7, 0
    swa r7, D_WRITE_INT
    ret

zp_check:
    jlt zero_pad
    ret

am:
    ldi r1, 'A'
    ret

pm:
    ldi r1, 'P'
    ret

suffix:
    jlt am
    jge pm

timecall:
    swa r9, D_SET_TIME_UNIT
    lwa r1, D_READ_TIME
    ret

unit:

    ; Colon
    ldi r7, ':'
    swa r7, D_WRITE_CHR

    ; Actual number
    ldi r2, 10
    cmp r1, r2      ; Check if we need to zero pad
    cal zp_check

    swa r1, D_WRITE_INT
    ret

reset:
    ldi r1, &escape
    swa r1, D_WRITE_STR

    ldi r1, '1'
    swa r1, D_WRITE_CHR

    ldi r1, '2'
    swa r1, D_WRITE_CHR

    ldi r1, 'D'
    swa r1, D_WRITE_CHR

    ret

clock:

    ; Fetch hour
    ldi r9, 3
    cal timecall

    ; Check for PM
    ldi r2, 12      ; PM = Past 12
    cmp r1, r2
    cal fix_hour_init

    ; Zero padding check
    ldi r2, 10
    cmp r1, r2
    cal zp_check

    ; Hour
    swa r1, D_WRITE_INT

    ; Minute
    ldi r9, 2
    cal timecall
    cal unit

    ; Second
    ldi r9, 1
    cal timecall
    cal unit

    ; PM
    ldi r9, 3
    cal timecall
    ldi r2, 12
    cmp r1, r2
    cal suffix

    ldi r2, ' '
    swa r2, D_WRITE_CHR
    swa r1, D_WRITE_CHR  ; A / P
    ldi r1, 'M'
    swa r1, D_WRITE_CHR
    ldi r1, '.'
    swa r1, D_WRITE_CHR

    ; Reset back to start of time section
    cal reset

    ; Sleep and repeat
    ldi r1, 500
    swa r1, D_SLEEP
    jmp clock

terminate:
    ldi r1, &show
    swa r1, D_WRITE_STR
    hlt

main:

    ; SIGINT
    ldi r1, 2
    swa r1, D_SIG_TARGET
    ldi r1, terminate
    swa r1, D_SIG_HOOK

    ; Hide cursor
    ldi r1, &invis
    swa r1, D_WRITE_STR

    ; Show current time message
    ldi r1, &time
    swa r1, D_WRITE_STR

    ; And start looping
    jmp clock
