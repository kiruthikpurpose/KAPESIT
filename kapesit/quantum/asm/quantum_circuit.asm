section .data
    H_GATE dd 0.707106781, 0.707106781, 0.707106781, -0.707106781
    X_GATE dd 0.0, 1.0, 1.0, 0.0
    Z_GATE dd 1.0, 0.0, 0.0, -1.0
    
section .bss
    circuit resd 16
    result resd 4

section .text
global _start

_start:
    ; Initialize quantum circuit
    mov eax, circuit
    call init_circuit
    
    ; Apply Hadamard gate
    mov eax, circuit
    mov ebx, H_GATE
    call apply_h_gate
    
    ; Apply Pauli-X gate
    mov eax, circuit
    mov ebx, X_GATE
    call apply_x_gate
    
    ; Apply Pauli-Z gate
    mov eax, circuit
    mov ebx, Z_GATE
    call apply_z_gate
    
    ; Measure final state
    mov eax, circuit
    mov ebx, result
    call measure_circuit
    
    ; Exit
    mov eax, 60
    xor edi, edi
    syscall

init_circuit:
    mov ecx, 16
    mov esi, circuit
    xor eax, eax
    loop_init:
        mov [esi], eax
        add esi, 4
        loop loop_init
    ret

apply_h_gate:
    ; Apply Hadamard transformation
    mov ecx, 4
    mov esi, circuit
    mov edi, result
    loop_h:
        push ecx
        mov ecx, 4
        mov ebx, H_GATE
        fldz
        loop_row:
            fld dword [ebx]
            fld dword [esi]
            fmul st0, st1
            fadd st2, st0
            fstp st0
            fstp st0
            add ebx, 4
            loop loop_row
        fstp dword [edi]
        add esi, 4
        add edi, 4
        pop ecx
        loop loop_h
    ret

apply_x_gate:
    ; Apply Pauli-X transformation
    mov ecx, 4
    mov esi, circuit
    mov edi, result
    loop_x:
        push ecx
        mov ecx, 4
        mov ebx, X_GATE
        fldz
        loop_row:
            fld dword [ebx]
            fld dword [esi]
            fmul st0, st1
            fadd st2, st0
            fstp st0
            fstp st0
            add ebx, 4
            loop loop_row
        fstp dword [edi]
        add esi, 4
        add edi, 4
        pop ecx
        loop loop_x
    ret

apply_z_gate:
    ; Apply Pauli-Z transformation
    mov ecx, 4
    mov esi, circuit
    mov edi, result
    loop_z:
        push ecx
        mov ecx, 4
        mov ebx, Z_GATE
        fldz
        loop_row:
            fld dword [ebx]
            fld dword [esi]
            fmul st0, st1
            fadd st2, st0
            fstp st0
            fstp st0
            add ebx, 4
            loop loop_row
        fstp dword [edi]
        add esi, 4
        add edi, 4
        pop ecx
        loop loop_z
    ret

measure_circuit:
    ; Measure quantum circuit
    mov ecx, 4
    mov esi, circuit
    mov edi, result
    loop_measure:
        fld dword [esi]
        fmul st0, st0
        fcomi st0, st1
        ja collapse
        add esi, 4
        loop loop_measure
    ret

collapse:
    ; Collapse quantum state
    mov eax, 1
    mov ebx, 0
    int 0x80
    ret
