extern "C" void vvadd(
    const float *a, const float *b, float *c,
    const unsigned n
) {

    #pragma HLS interface m_axi port=a offset=slave bundle=gmem
    #pragma HLS interface m_axi port=b offset=slave bundle=gmem
    #pragma HLS interface m_axi port=c offset=slave bundle=gmem
    #pragma HLS interface s_axilite port=a bundle=control
    #pragma HLS interface s_axilite port=b bundle=control
    #pragma HLS interface s_axilite port=c bundle=control
    #pragma HLS interface s_axilite port=n bundle=control
    #pragma HLS interface s_axilite port=return bundle=control

    for (unsigned i = 0; i < n; ++i) {
        #pragma HLS PIPELINE II=1
        c[i] = a[i] + b[i];
    }
}
