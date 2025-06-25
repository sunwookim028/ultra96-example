extern "C" void vvdot(
    const int *a, const int *b,
    const unsigned n,
    int& result
) {

    #pragma HLS interface m_axi port=a offset=slave bundle=gmem_a
    #pragma HLS interface m_axi port=b offset=slave bundle=gmem_b
    #pragma HLS interface s_axilite port=a bundle=control
    #pragma HLS interface s_axilite port=b bundle=control
    #pragma HLS interface s_axilite port=n bundle=control
    #pragma HLS interface s_axilite port=result bundle=control
    #pragma HLS interface s_axilite port=return bundle=control

    int acc = 0;
    for (unsigned i = 0; i < n; ++i) {
        #pragma HLS PIPELINE II=1
        acc += a[i] * b[i];
    }
    result = acc;
}
