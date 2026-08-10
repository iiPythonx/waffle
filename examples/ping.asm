; Copyright (c) 2026 iiPython

preload:
    host:        .string "1.1.1.1"
    ping:        .string "PING "
    failure:     .string "The client received an invalid response.\n"
    packet_size: .string "size="
    packet_seq:  .string "icmp_seq="
    packet_time: .string "time="
    packet_ms:   .string " ms"

generate_checksum_loop:

    ; fetch bytes
    ldi r4, 0x2500
    add r4, r2
    lwr r5, r4

    ; update accumulator
    mov r6, r3
    add r3, r5
    cmp r3, r6
    jge skip_checksum_increment

    ldi r6, 1
    add r3, r6

    skip_checksum_increment:

    ; increment for next iteration
    inc r2
    inc r2

    cmp r2, r1
    jge skip_checksum_loop

    jmp generate_checksum_loop

    skip_checksum_loop:
    not r3
    ret

generate_checksum:

    ; calculate size
    ; r1 = data size
    ldi r2, 0x2500
    sub r1, r2

    ; padding
    ; r2 = modulo result (for padding)
    mov r2, r1
    mov r4, r1
    ldi r3, 2
    div r4, r3
    mul r4, r3
    sub r2, r4

    ldi r3, 0
    cmp r2, r3
    jeq skip_checksum_padding

    ldi r2, 0x2500
    add r2, r1
    ldi r3, 0
    sbr r3, r2

    skip_checksum_padding:

    ; loop
    ; r1 = data size
    ; r2 = counter
    ; r3 = accumulator
    ldi r2, 0
    ldi r3, 0

    cal generate_checksum_loop

    ; r2 = checksum
    mov r2, r3
    ret

generate_packet:
    ldi r1, 0x2500  ; memory region

    ; type 8 = echo
    ldi r2, 8
    sbr r2, r1
    inc r1

    ; code
    ldi r2, 0
    sbr r2, r1
    inc r1

    ; checksum (temp)
    sbr r2, r1
    inc r1
    sbr r2, r1
    inc r1

    ; id
    ldi r2, 1
    swr r2, r1
    inc r1
    inc r1

    ; sequence
    lwa r2, 0x2450
    inc r2           ; our sequence in memory starts at 0, so increment here
    swr r2, r1
    inc r1
    inc r1

    ; payload
    ldi r2, 'P'
    sbr r2, r1
    inc r1

    ldi r2, 'I'
    sbr r2, r1
    inc r1

    ldi r2, 'N'
    sbr r2, r1
    inc r1

    ldi r2, 'G'
    sbr r2, r1
    inc r1

    mov r9, r1

    ; calculate checksum
    cal generate_checksum

    ldi r1, 0x2502  ; checksum portion
    swr r2, r1

    ; place write offset back into r1
    mov r1, r9
    ret

send_ping:

    ; generate packet
    cal generate_packet

    ldi r3, 0x2500
    sub r1, r3

    ldi r2, 5
    swa r2, D_SELECT_NET_VARIABLE
    swa r1, D_WRITE_NET_VARIABLE

    ldi r2, 4
    swa r2, D_SELECT_NET_VARIABLE
    swa r3, D_WRITE_NET_VARIABLE

    ; set host and port
    ldi r1, 6
    swa r1, D_SELECT_NET_VARIABLE
    ldi r1, &host
    swa r1, D_WRITE_NET_VARIABLE

    ldi r1, 7
    swa r1, D_SELECT_NET_VARIABLE
    ldi r1, 0
    swa r1, D_WRITE_NET_VARIABLE

    ; send packet
    swa r1, D_ZERO_CLOCK
    swa r1, D_NET_SEND

    ; receive packet
    ldi r1, 8
    swa r1, D_SELECT_NET_VARIABLE
    ldi r1, 0x2600
    swa r1, D_WRITE_NET_VARIABLE

    lwa r4, D_NET_RECEIVE
    lwa r5, D_READ_ELAPSED

    ldi r2, 20
    add r1, r2

    ; validate response type
    lbr r2, r1
    ldi r3, 0
    cmp r2, r3
    jeq skip_response_type_abort

    ldi r1, &failure
    swa r1, D_WRITE_STR
    hlt

    skip_response_type_abort:

    ; grab sequence id
    ldi r2, 6
    add r1, r2
    lwr r2, r1

    ; logging
    ldi r1, &host
    swa r1, D_WRITE_STR
    ldi r1, ':'
    swa r1, D_WRITE_CHR
    ldi r1, ' '
    swa r1, D_WRITE_CHR

    ldi r1, &packet_size
    swa r1, D_WRITE_STR
    swa r4, D_WRITE_INT
    ldi r1, ' '
    swa r1, D_WRITE_CHR

    ldi r1, &packet_seq
    swa r1, D_WRITE_STR
    swa r2, D_WRITE_INT
    ldi r1, ' '
    swa r1, D_WRITE_CHR

    ldi r1, &packet_time
    swa r1, D_WRITE_STR
    swa r5, D_WRITE_INT
    ldi r1, &packet_ms
    swa r1, D_WRITE_STR
    ldi r2, 10
    swa r2, D_WRITE_CHR

    ; increment sequence
    lwa r1, 0x2450
    inc r1
    swa r1, 0x2450

    ; sleep and go again
    ldi r1, 1000
    swa r1, D_SLEEP

    jmp send_ping

terminate:
    swa r1, D_CLOSE_SOCKET
    hlt

main:

    ; interface
    ldi r1, &ping
    swa r1, D_WRITE_STR
    ldi r1, &host
    swa r1, D_WRITE_STR
    ldi r1, 10
    swa r1, D_WRITE_CHR

    ; create socket
    ldi r1, 1
    ldi r2, 2
    swa r1, D_SELECT_NET_VARIABLE
    swa r2, D_WRITE_NET_VARIABLE

    ldi r1, 2
    ldi r2, 3
    swa r1, D_SELECT_NET_VARIABLE
    swa r2, D_WRITE_NET_VARIABLE

    ldi r1, 3
    ldi r2, 1
    swa r1, D_SELECT_NET_VARIABLE
    swa r2, D_WRITE_NET_VARIABLE

    swa r1, D_CREATE_SOCKET

    ; begin sending pings
    jmp send_ping
