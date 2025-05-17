section .text
global fast_dot_product
global fast_matrix_transpose
global fast_vector_norm
global fast_convolution

fast_dot_product:
    push rbp
    mov rbp, rsp
    
    mov rcx, rdx
    xorps xmm0, xmm0
    
.loop:
    movups xmm1, [rdi]
    movups xmm2, [rsi]
    mulps xmm1, xmm2
    addps xmm0, xmm1
    
    add rdi, 16
    add rsi, 16
    sub rcx, 4
    jnz .loop
    
    haddps xmm0, xmm0
    haddps xmm0, xmm0
    
    movss [r8], xmm0
    
    pop rbp
    ret

fast_matrix_transpose:
    push rbp
    mov rbp, rsp
    
    mov rcx, rdx
.outer_loop:
    mov rdx, rcx
.inner_loop:
    movups xmm0, [rdi]
    movups xmm1, [rdi + 16]
    movups xmm2, [rdi + 32]
    movups xmm3, [rdi + 48]
    
    movaps xmm4, xmm0
    movaps xmm5, xmm1
    movaps xmm6, xmm2
    movaps xmm7, xmm3
    
    shufps xmm0, xmm2, 0x88
    shufps xmm1, xmm3, 0x88
    shufps xmm2, xmm4, 0xDD
    shufps xmm3, xmm5, 0xDD
    
    movups [rsi], xmm0
    movups [rsi + 16], xmm1
    movups [rsi + 32], xmm2
    movups [rsi + 48], xmm3
    
    add rdi, 64
    add rsi, 64
    sub rdx, 4
    jnz .inner_loop
    
    sub rcx, 4
    jnz .outer_loop
    
    pop rbp
    ret

fast_vector_norm:
    push rbp
    mov rbp, rsp
    
    mov rcx, rsi
    xorps xmm0, xmm0
    
.norm_loop:
    movups xmm1, [rdi]
    mulps xmm1, xmm1
    addps xmm0, xmm1
    
    add rdi, 16
    sub rcx, 4
    jnz .norm_loop
    
    haddps xmm0, xmm0
    haddps xmm0, xmm0
    sqrtss xmm0, xmm0
    
    movss [rdx], xmm0
    
    pop rbp
    ret

fast_convolution:
    push rbp
    mov rbp, rsp
    
    mov rcx, rdx
    mov rdx, rcx
    
.conv_loop:
    movups xmm0, [rdi]
    movups xmm1, [rsi]
    mulps xmm0, xmm1
    addps xmm2, xmm0
    
    add rdi, 16
    add rsi, 16
    sub rcx, 4
    jnz .conv_loop
    
    haddps xmm2, xmm2
    haddps xmm2, xmm2
    
    movss [r8], xmm2
    
    pop rbp
    ret 