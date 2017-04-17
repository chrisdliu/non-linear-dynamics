//
//  clib.cpp
//  clib
//
//  Created by Chris Liu on 4/6/17.
//  Copyright © 2017 Chris Liu. All rights reserved.
//


typedef unsigned char uchar;


extern "C" void turn(uchar** world, uchar** alt, bool swap, int r, int c, int iter, uchar lookup[512]) {
    uchar** src;
    uchar** dest;
    
    for (int it = 0; it < iter; it++) {
        if (!swap) {
            src = world;
            dest = alt;
        } else {
            src = alt;
            dest = world;
        }
        
    #pragma omp parallel for
        for (int x = 1; x < r - 1; x++) {
            for (int y = 1; y < c - 1; y++) {
                int hash = src[x - 1][y - 1] << 8 | src[x - 1][y] << 7 |
                           src[x - 1][y + 1] << 6 | src[x][y - 1] << 5 |
                           src[x][y + 1] << 4 | src[x + 1][y - 1] << 3 |
                           src[x + 1][y] << 2 | src[x + 1][y + 1] << 1 |
                           src[x][y];
                dest[x][y] = lookup[hash];
            }
        }
        
        swap = !swap;
    }
}
