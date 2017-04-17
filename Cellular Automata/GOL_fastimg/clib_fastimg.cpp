//
//  clib.cpp
//  clib
//
//  Created by Chris Liu on 4/6/17.
//  Copyright © 2017 Chris Liu. All rights reserved.
//


#include <stdio.h>
#include <cstring>


typedef unsigned char uchar;


/**
 Fills a white region with purple.
 */
extern "C" void fill(uchar* pixels, int iw, int x0, int y0, int x1, int y1) {
    for (int y = y0; y < y1; y++) {
        int idx = (y * iw + x0) * 3;
        for (int x = x0; x < x1; x++) {
            pixels[idx + 1] = 0;
            idx += 3;
        }
    }
}

extern "C" void rect(uchar* pixels, int iw, int x0, int y0, int w, int h) {
    int x1 = x0 + w;
    int y1 = y0 + h;
    for (int y = y0; y < y1; y++) {
        int idx = (y * iw + x0) * 3;
        for (int x = x0; x < x1; x++) {
            pixels[idx + 1] = 0;
            idx += 3;
        }
    }
}


/**
 world - world to be drawn
 r, c - world's rows and columns
 pixels - image's width and height
 w, h - image's width and height
 s - side length of a cell (has to be even)
 cx, cy - center tile of the view
 */
extern "C" void set_pixels(uchar** world, int r, int c, uchar* pixels, int w, int h, int s, int cx, int cy) {
    
    memset(pixels, 255, w * h * 3);
    
    //pre calculate this stuff later
    //even width and height
    int ew = w - w % 2, eh = h - h % 2;
    int rows = eh / s + 1;
    int cols = ew / s + 1;
    //make rows and cols odd
    if (!(rows % 2)) {
        rows++;
    }
    if (!(cols % 2)) {
        cols++;
    }
    
    //edge rows and cols
    int r0 = cy - rows / 2;
    int r1 = cy + rows / 2;
    int c0 = cx - cols / 2;
    int c1 = cx + cols / 2;
    
    //corner flags: NW, NE, SW, SE
    uchar flags = 0xf;
    uchar NW = 0x8, NE = 0x4, SW = 0x2, SE = 0x1;
    if (r0 < 1) {
        flags &= ~(SW | SE); //0xc
        r0 = 1;
    }
    if (r1 > r - 2) {
        flags &= ~(NW | NE); //0x3
        r1 = r - 2;
    }
    if (c0 < 1) {
        flags &= ~(NW | SW); //0x5
        c0 = 1;
    }
    if (c1 > c - 2) {
        flags &= ~(NE | SE); //0xa
        c1 = c - 2;
    }
    
    //image center
    int icx = ew / 2, icy = eh / 2;
    //half side
    int hs = s / 2;
    //inner square bounds
    int ix0 = icx - hs - s * (cx - c0 - 1);
    int iy0 = icy - hs - s * (cy - r0 - 1);
    int ix1 = icx + hs + s * (c1 - cx - 1);
    int iy1 = icy + hs + s * (r1 - cy - 1);
    
    //corners
    if (flags & NW) {
        if (world[r1][c0]) {
            fill(pixels, w, 0, iy1, ix0, eh);
        }
    }
    if (flags & NE) {
        if (world[r1][c1]) {
            fill(pixels, w, ix1, iy1, ew, eh);
        }
    }
    if (flags & SW) {
        if (world[r0][c0]) {
            fill(pixels, w, 0, 0, ix0, iy0);
        }
    }
    if (flags & SE) {
        if (world[r0][c1]) {
            fill(pixels, w, ix1, 0, ew, iy0);
        }
    }
    
    //edges - top, bottom, left, right
    if (flags & (NW | NE)) {
        for (int i = c0 + 1; i < c1; i++) {
            if (world[r1][i]) {
                rect(pixels, w, ix0 + s * (i - c0 - 1), iy1, s, eh - iy1);
            }
        }
    }
    if (flags & (SW | SE)) {
        for (int i = c0 + 1; i < c1; i++) {
            if (world[r0][i]) {
                rect(pixels, w, ix0 + s * (i - c0 - 1), 0, s, iy0);
            }
        }
    }
    if (flags & (NW | SW)) {
        for (int i = r0 + 1; i < r1; i++) {
            if (world[i][c0]) {
                rect(pixels, w, 0, iy0 + s * (i - r0 - 1), ix0, s);
            }
        }
    }
    if (flags & (NE | SE)) {
        for (int i = r0 + 1; i < r1; i++) {
            if (world[i][c1]) {
                rect(pixels, w, ix1, iy0 + s * (i - r0 - 1), ew - ix1, s);
            }
        }
    }
    
    //inner square
    for (int y = r0 + 1; y < r1; y++) {
        for (int x = c0 + 1; x < c1; x++) {
            if (world[y][x]) {
                rect(pixels, w, ix0 + s * (x - c0 - 1), iy0 + s * (y - r0 - 1), s, s);
            }
        }
    }
}


/**
 world, alt - simulation grid with gutters
 swap - determines source and destination worlds
 r, c - world's rows and columns
 iter - amount of iterations to run
 lookup - predetermined rule hashtable
 pixels - image's pixel array
 w, h - image's width and height
 s - side lnegth of a cell
 cx, cy - center tile of the view
 */
extern "C" void turn(uchar** world, uchar** alt, bool swap, int r, int c, int iter, uchar* lookup, uchar* pixels, int w, int h, int s, int cx, int cy) {
    
    uchar** src = nullptr;
    uchar** dest = nullptr;
    
    for (int it = 0; it < iter; it++) {
        if (!swap) {
            src = world;
            dest = alt;
        } else {
            src = alt;
            dest = world;
        }
        
    #pragma omp parallel for
        for (int y = 1; y < r - 1; y++) {
            for (int x = 1; x < c - 1; x++) {
                int hash = src[y - 1][x - 1] << 8 | src[y - 1][x] << 7 |
                           src[y - 1][x + 1] << 6 | src[y][x - 1] << 5 |
                           src[y][x + 1] << 4 | src[y + 1][x - 1] << 3 |
                           src[y + 1][x] << 2 | src[y + 1][x + 1] << 1 |
                           src[y][x];
                dest[y][x] = lookup[hash];
            }
        }
        
        swap = !swap;
    }
    
    set_pixels(dest, r, c, pixels, w, h, s, cx, cy);
}
