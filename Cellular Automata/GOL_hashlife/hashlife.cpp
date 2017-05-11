//
//  hashlife.cpp
//  hashlife
//
//  Created by Chris Liu on 4/9/17.
//  Copyright © 2017 Chris Liu. All rights reserved.
//

/**
 Todo:
 
 better hash function
 */

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <limits.h>

#include "hashlife.h"


using namespace std;


//Node class
//must call set base nodes before anything

Node::Node(Node* nw, Node* ne, Node* sw, Node* se) {
    this->nw = nw;
    this->ne = ne;
    this->sw = sw;
    this->se = se;
    this->future = nullptr;
    this->next = nullptr;
    
    if (nw && ne && sw && se) {
        this->pop = nw->pop + ne->pop + sw->pop + se->pop;
    } else {
        this->pop = 0;
    }
}

Node::~Node() {
    Future* curr = this->future;
    Future* next;
    while (curr) {
        next = curr->next;
        delete curr;
        curr = next;
    }
}

bool Node::alive() {
    return (this == Node::LVL0[1]);
}

int Node::level() {
    int level = 0;
    Node* curr = this;
    while (curr->nw) {
        curr = curr->nw;
        level++;
    }
    return level;
}

bool Node::contains(Node* node) {
    if (node->level() >= this->level() || node->level() == 2) {
        return node == this;
    } else {
        if (this->nw->contains(node)) {
            return true;
        }
        if (this->ne->contains(node)) {
            return true;
        }
        if (this->sw->contains(node)) {
            return true;
        }
        if (this->se->contains(node)) {
            return true;
        }
        return false;
    }
}

Node* Node::expand(HashTable* hashtable) {
    int zero_level = this->level() - 1;
    Node* zero_node = Node::zero_node(hashtable, zero_level);
    Node* nw = hashtable->get(zero_node, zero_node, zero_node, this->nw);
    Node* ne = hashtable->get(zero_node, zero_node, this->ne, zero_node);
    Node* sw = hashtable->get(zero_node, this->sw, zero_node, zero_node);
    Node* se = hashtable->get(this->se, zero_node, zero_node, zero_node);
    return hashtable->get(nw, ne, sw, se);
}

Node* Node::compact(HashTable* hashtable) {
    if (this->level() < 3) {
        return this;
    }
    
    int zero_level = this->level() - 2;
    Node* zero_node = Node::zero_node(hashtable, zero_level);
    
    if (this->nw->nw == zero_node && this->nw->ne == zero_node && this->nw->sw == zero_node && \
        this->ne->nw == zero_node && this->ne->ne == zero_node && this->ne->se == zero_node && \
        this->sw->nw == zero_node && this->sw->sw == zero_node && this->sw->se == zero_node && \
        this->se->ne == zero_node && this->se->sw == zero_node && this->se->se == zero_node) {
        return Node::center(hashtable, this)->compact(hashtable);
    } else {
        return this;
    }
}

Node* Node::turn(HashTable* hashtable, int power) {
    int level = this->level();
    if (power >= level - 2) {
        //turn twice for exponential speedup
        
        Node* future_node = this->get_future(level - 2);
        if (future_node) {
            return future_node;
        }
        
        Node* n00 = this->nw->turn(hashtable, power);
        Node* n01 = Node::horizontal(hashtable, this->nw, this->ne)->turn(hashtable, power);
        Node* n02 = this->ne->turn(hashtable, power);
        Node* n10 = Node::vertical(hashtable, this->nw, this->sw)->turn(hashtable, power);
        Node* n11 = Node::center(hashtable, this)->turn(hashtable, power);
        Node* n12 = Node::vertical(hashtable, this->ne, this->se)->turn(hashtable, power);
        Node* n20 = this->sw->turn(hashtable, power);
        Node* n21 = Node::horizontal(hashtable, this->sw, this->se)->turn(hashtable, power);
        Node* n22 = this->se->turn(hashtable, power);
        
        future_node = hashtable->get(hashtable->get(n00, n01, n10, n11)->turn(hashtable, power),
                                      hashtable->get(n01, n02, n11, n12)->turn(hashtable, power),
                                      hashtable->get(n10, n11, n20, n21)->turn(hashtable, power),
                                      hashtable->get(n11, n12, n21, n22)->turn(hashtable, power));
        
        //add future
        this->add_future(future_node, level - 2);
        return future_node;
    } else {
        //turn only once
        Node* future_node = this->get_future(power);
        if (future_node) {
            return future_node;
        }
        
        Node* n00 = Node::center(hashtable, this->nw);
        Node* n01 = Node::horizontal_center(hashtable, this->nw, this->ne);
        Node* n02 = Node::center(hashtable, this->ne);
        Node* n10 = Node::vertical_center(hashtable, this->nw, this->sw);
        Node* n11 = Node::center(hashtable, Node::center(hashtable, this));
        Node* n12 = Node::vertical_center(hashtable, this->ne, this->se);
        Node* n20 = Node::center(hashtable, this->sw);
        Node* n21 = Node::horizontal_center(hashtable, this->sw, this->se);
        Node* n22 = Node::center(hashtable, this->se);
        
        future_node = hashtable->get(hashtable->get(n00, n01, n10, n11)->turn(hashtable, power),
                                      hashtable->get(n01, n02, n11, n12)->turn(hashtable, power),
                                      hashtable->get(n10, n11, n20, n21)->turn(hashtable, power),
                                      hashtable->get(n11, n12, n21, n22)->turn(hashtable, power));
        
        //add future
        this->add_future(future_node, power);
        return future_node;
    }
}

void Node::add_future(Node* node, int power) {
    if (this->future) {
        Future* future = new Future(node, power);
        future->next = this->future;
        this->future = future;
    } else {
        this->future = new Future(node, power);
    }
}

Node* Node::get_future(int power) {
    Future* curr = this->future;
    while (curr) {
        if (curr->power == power) {
            return curr->node;
        }
        curr = curr->next;
    }
    return nullptr;
}

Node* Node::center(HashTable* hashtable, Node* node) {
    return hashtable->get(node->nw->se, node->ne->sw, node->sw->ne, node->se->nw);
}

Node* Node::horizontal(HashTable* hashtable, Node* left, Node* right) {
    return hashtable->get(left->ne, right->nw, left->se, right->sw);
}

Node* Node::vertical(HashTable* hashtable, Node* up, Node* down) {
    return hashtable->get(up->sw, up->se, down->nw, down->ne);
}

Node* Node::horizontal_center(HashTable* hashtable, Node* left, Node* right) {
    return hashtable->get(left->ne->se, right->nw->sw, left->se->ne, right->sw->nw);
}

Node* Node::vertical_center(HashTable* hashtable, Node* up, Node* down) {
    return hashtable->get(up->sw->se, up->se->sw, down->nw->ne, down->ne->nw);
}

uint Node::hash(Node* nw, Node* ne, Node* sw, Node* se) {
    return (uint)((((5381 * 31 + (ulong)nw) * 31 + (ulong)ne) * 31 + (ulong)sw) * 31 + (ulong)se);
}

void Node::set_base_nodes(int bflags, int sflags) {
    //2^2^(2*0) = 2
    Node::LVL0 = new Node* [2] { new Node(0, 0, 0, 0), new Node(0, 0, 0, 0) };
    Node::LVL0[1]->pop = 1;
    Node** LVL0 = Node::LVL0;
    
    //2^2^(2*1) = 16
    Node::LVL1 = new Node* [16];
    for (int i = 0; i < 16; i++) {
        Node::LVL1[i] = new Node(LVL0[i >> 3], LVL0[i >> 2 & 1], LVL0[i >> 1 & 1], LVL0[i & 1]);
    }
    Node** LVL1 = Node::LVL1;
    
    //offset for calculating neighbor count
    int o[4] = { 0, 1, 4, 5 };
    //2^2^(2*2) = 65536
    Node::LVL2 = new Node* [65536];
    for (int i = 0; i < 65536; i++) {
        Node::LVL2[i] = new Node(LVL1[(i >> 12 & 12) | (i >> 10 & 3)], LVL1[(i >> 10 & 12) | (i >> 8 & 3)],
                                 LVL1[(i >> 4 & 12) | (i >> 2 & 3)], LVL1[(i >> 2 & 12) | (i & 3)]);
        int future_idx = 0;
        for (int j = 0; j < 4; j++) {
            int count = ((i >> (10 + o[j]) & 1) + (i >> (9 + o[j]) & 1) + (i >> (8 + o[j]) & 1) + (i >> (6 + o[j]) & 1) +
                         (i >> (4 + o[j]) & 1) + (i >> (2 + o[j]) & 1) + (i >> (1 + o[j]) & 1) + (i >> o[j] & 1));
            if (i >> (5 + o[j]) & 1) {
                //center alive
                if ((sflags >> count) & 1) {
                    future_idx |= 1 << j;
                }
            } else {
                //center dead
                if ((bflags >> count) & 1) {
                    future_idx |= 1 << j;
                }
            }
        }
        Node::LVL2[i]->add_future(Node::LVL1[future_idx], 0);
    }
}

void Node::delete_base_nodes() {
    //content in array would be deleted by hashtable->clear()
    delete Node::LVL0;
    delete Node::LVL1;
    delete Node::LVL2;
}

Node* Node::zero_node(HashTable* hashtable, int level) {
    if (level == 0) {
        return Node::LVL0[0];
    }
    if (level == 1) {
        return Node::LVL1[0];
    }
    if (level == 2) {
        return Node::LVL2[0];
    }
    
    Node* zero_node = Node::LVL2[0];
    for (int i = 2; i < level; i++) {
        zero_node = hashtable->get(zero_node, zero_node, zero_node, zero_node);
    }
    
    return zero_node;
}

//Future

Future::Future(Node* node, int power) {
    this->node = node;
    this->power = power;
    this->next = nullptr;
}

Future::~Future() {
}


//HashTable

HashTable::HashTable() : hashprime(196613), hashcount(0) {
    this->table = new Node* [this->hashprime] { };
}

HashTable::~HashTable() {
    //content in table would be deleted by hashtable->clear()
    delete this->table;
}

//deletes all nodes in hashtable
void HashTable::clear() {
    Node* curr;
    Node* next;
    for (int i = 0; i < this->hashprime; i++) {
        curr = this->table[i];
        while (curr) {
            next = curr->next;
            delete curr;
            curr = next;
        }
    }
    this->hashcount = 0;
}

void HashTable::clean(Node* root) {
    Node* curr;
    Node* next;
    Node* prev = nullptr;
    for (int i = 0; i < this->hashprime; i++) {
        curr = this->table[i];
        this->table[i] = nullptr;
        while (curr) {
            if (root->contains(curr)) {
                if (prev) {
                    prev->next = curr;
                } else {
                    this->table[i] = curr;
                }
                prev = curr;
                curr = curr->next;
            } else {
                next = curr->next;
                delete curr;
                curr = next;
            }
        }
    }
}

void HashTable::add(Node* node) {
    int hash = Node::hash(node->nw, node->ne, node->sw, node->se) % this->hashprime;
    if (this->table[hash]) {
        node->next = this->table[hash];
    }
    this->table[hash] = node;
    this->hashcount++;
}

//searches hashtable for match
//if no match, creates new node
//all quadrants pointers have to be non-zero
Node* HashTable::get(Node* nw, Node* ne, Node* sw, Node* se) {
    if (!(nw && ne && sw && se)) {
        return nullptr;
    }
    
    int hash = Node::hash(nw, ne, sw, se) % this->hashprime;
    Node* res = nullptr;
    Node* curr = this->table[hash];
    while (curr) {
        if (curr->nw == nw && curr->ne == ne && curr->sw == sw && curr->se == se) {
            res = curr;
            break;
        }
        curr = curr->next;
    }
    
    if (!res) {
        //create new node
        res = new Node(nw, ne, sw, se);
        this->add(res);
    }
    
    return res;
}

void HashTable::add_base_nodes(HashTable* hashtable) {
    Node** LVL0 = Node::LVL0;
    Node** LVL1 = Node::LVL1;
    Node** LVL2 = Node::LVL2;
    
    hashtable->add(LVL0[0]);
    hashtable->add(LVL0[1]);
    
    for (int i = 0; i < 16; i++) {
        hashtable->add(LVL1[i]);
    }
    
    for (int i = 0; i < 65536; i++) {
        hashtable->add(LVL2[i]);
    }
}

void HashTable::report() {
    printf("Hashtable report:\n");
    int min = this->hashcount, max = 0, empty = 0;
    for (int i = 0; i < this->hashprime; i++) {
        int length = 0;
        Node* curr = this->table[i];
        if (!curr) {
            empty++;
            min = 0;
            continue;
        }
        while (curr) {
            curr = curr->next;
            length++;
        }
        if (length < min) {
            min = length;
        }
        if (length > max) {
            max = length;
        }
    }
    printf("\tMin: %d\n", min);
    printf("\tMax: %d\n", max);
    printf("\tEmpty percent: %f\n\n", (float)empty * 100 / this->hashprime);
}



Node* turn(HashTable* hashtable, Node* root, long n) {
    printf("Turning %ld generations...\n", n);
    int power = 0;
    while (n) {
        if (n & 1) {
            int level = root->level();
            printf("\tPower: %d\t", power);
            printf("Level: %d\t", root->level());
            // expanding a times gives at least 2^(n+a-2) room to grow on the side
            // turning p times needs 2^p extra side width
            for (int i = 0; i < power - level; i++) {
                root = root->expand(hashtable);
            }
            printf("Expanding... ");
            root = root->expand(hashtable)->expand(hashtable);
            printf("%d\t", root->level());
            printf("Turning...\t");
            root = root->turn(hashtable, power);
            printf("Compacting... ");
            root = root->compact(hashtable);
            printf("%d\t", root->level());
            printf("Hashcount: %d\n", hashtable->hashcount);
        }
        n >>= 1;
        power++;
    }
    return root;
}

extern "C" {
    HashTable* init(int bflags, int sflags) {
        HashTable* hashtable = new HashTable();
        Node::set_base_nodes(bflags, sflags);
        return hashtable;
    }
    
    Node* get_root(HashTable* hashtable) {
        return new Node(Node::LVL2[0], Node::LVL2[0], Node::LVL2[0], Node::LVL2[0]);
    }
    
    Node* add_root(HashTable* hashtable, Node* root) {
        if (root->level() == 3) {
            return hashtable->get(root->nw, root->ne, root->sw, root->se);
        } else {
            return hashtable->get(add_root(hashtable, root->nw), add_root(hashtable, root->ne), add_root(hashtable, root->sw), add_root(hashtable, root->se));
        }
    }
    
    HashTable* start(HashTable* hashtable, Node* root) {
        delete hashtable;
        hashtable = new HashTable();
        add_root(hashtable, root);
        HashTable::add_base_nodes(hashtable);
        return hashtable;
    }
    
    Node* run(HashTable* hashtable, Node* root, long n) {
        mark();
        root = turn(hashtable, root, n);
        long time = mark();
        printf("\tTurn time: %ldms\n\n", time);
        return root;
    }
    
    void end(HashTable* hashtable) {
        hashtable->report();
        hashtable->clear();
        delete hashtable;
        Node::delete_base_nodes();
    }
    
    int node_level(Node* node) {
        return node->level();
    }
    
    long node_pop(Node* node) {
        return node->pop;
    }
    
    int hashtable_count(HashTable* hashtable) {
        return hashtable->hashcount;
    }
    
    bool get_cell(Node* root, long x, long y) {
        long max = powl(2, root->level() - 1);
        if (root->level() > 63 || !(-max <= x && x < max && -max <= y && y < max)) {
            return false;
        }
        if (root->level() < 2) {
            if (root->level() != 1) {
                return false;
            }
            if (x < 0) {
                if (y < 0) {
                    return root->sw->alive();
                } else {
                    return root->nw->alive();
                }
            } else {
                if (y < 0) {
                    return root->se->alive();
                } else {
                    return root->ne->alive();
                }
            }
        } else {
            long offset = powl(2, root->level() - 2);
            if (x < 0) {
                if (y < 0) {
                    return get_cell(root->sw, x + offset, y + offset);
                } else {
                    return get_cell(root->nw, x + offset, y - offset);
                }
            } else {
                if (y < 0) {
                    return get_cell(root->se, x - offset, y + offset);
                } else {
                    return get_cell(root->ne, x - offset, y - offset);
                }
            }
        }
    }
    
    //only call before running
    Node* set_cell_recurs(HashTable* hashtable, Node* root, long x, long y, bool state);
    Node* set_cell(HashTable* hashtable, Node* root, long x, long y, bool state) {
        long max = powl(2, root->level() - 1);
        while (!(-max <= x && x < max && -max <= y && y < max)) {
            root = root->expand(hashtable);
            max = powl(2, root->level() - 1);
            printf("Expanding...\n");
        }
        root = set_cell_recurs(hashtable, root, x, y, state);
        return root;
    }
    
    Node* set_cell_recurs(HashTable* hashtable, Node* root, long x, long y, bool state) {
        if (root->level() < 4) {
            //don't add any lvl 2 nodes to the hashtable!!!
            if (root->level() != 3) {
                return root;
            }
            Node* old2;
            long x2, y2;
            if (x < 0) {
                if (y < 0) {
                    old2 = root->sw;
                    x2 = x + 2;
                    y2 = y + 2;
                } else {
                    old2 = root->nw;
                    x2 = x + 2;
                    y2 = y - 2;
                }
            } else {
                if (y < 0) {
                    old2 = root->se;
                    x2 = x - 2;
                    y2 = y + 2;
                } else {
                    old2 = root->ne;
                    x2 = x - 2;
                    y2 = y - 2;
                }
            }
            int sig = ((old2->nw->nw->alive() << 15) | (old2->nw->ne->alive() << 14) | (old2->ne->nw->alive() << 13) | (old2->ne->ne->alive() << 12) |
                       (old2->nw->sw->alive() << 11) | (old2->nw->se->alive() << 10) | (old2->ne->sw->alive() << 9) | (old2->ne->se->alive() << 8) |
                       (old2->sw->nw->alive() << 7) | (old2->sw->ne->alive() << 6) | (old2->se->nw->alive() << 5) | (old2->se->ne->alive() << 4) |
                       (old2->sw->sw->alive() << 3) | (old2->sw->se->alive() << 2) | (old2->se->sw->alive() << 1) | (old2->se->se->alive()));
            int o[4][4] = {
                { 3, 7, 11, 15 },
                { 2, 6, 10, 14 },
                { 1, 5, 9, 13 },
                { 0, 4, 8, 12 }
            };
            sig ^= (-state ^ sig) & (1 << o[x2 + 2][y2 + 2]);
            if (x < 0) {
                if (y < 0) {
                    root = hashtable->get(root->nw, root->ne, Node::LVL2[sig], root->se);
                } else {
                    root = hashtable->get(Node::LVL2[sig], root->ne, root->sw, root->se);
                }
            } else {
                if (y < 0) {
                    root = hashtable->get(root->nw, root->ne, root->sw, Node::LVL2[sig]);
                } else {
                    root = hashtable->get(root->nw, Node::LVL2[sig], root->sw, root->se);
                }
            }
            
            return root;
        } else {
            long offset = powl(2, root->level() - 2);
            if (x < 0) {
                if (y < 0) {
                    Node* sw = set_cell_recurs(hashtable, root->sw, x + offset, y + offset, state);
                    root = hashtable->get(root->nw, root->ne, sw, root->se);
                } else {
                    Node* nw = set_cell_recurs(hashtable, root->nw, x + offset, y - offset, state);
                    root = hashtable->get(nw, root->ne, root->sw, root->se);
                }
            } else {
                if (y < 0) {
                    Node* se = set_cell_recurs(hashtable, root->se, x - offset, y + offset, state);
                    root = hashtable->get(root->nw, root->ne, root->sw, se);
                } else {
                    Node* ne = set_cell_recurs(hashtable, root->ne, x - offset, y - offset, state);
                    root = hashtable->get(root->nw, ne, root->sw, root->se);
                }
            }
            
            return root;
        }
    }
    
    void fill(uchar* pixels, int iw, long x0, long y0, long x1, long y1) {
        for (long y = y0; y < y1; y++) {
            long idx = (y * iw + x0) * 3;
            for (long x = x0; x < x1; x++) {
                pixels[idx + 1] = 0;
                idx += 3;
            }
        }
    }
    
    void rect(uchar* pixels, int iw, long x0, long y0, long w, long h) {
        fill(pixels, iw, x0, y0, x0 + w, y0 + h);
    }
    
    void clear_pixels(uchar* pixels, int w, int h, uchar color) {
        memset(pixels, color, w * h * 3);
    }
    
    /*
     cx, cy - center x, center y
     ss - square size
     */
    void set_pixels(uchar* pixels, int w, int h, Node* root, long cx, long cy, int ss) {
        //set pixels to white
        memset(pixels, 255, w * h * 3);
        
        //ew, eh - even width and even height
        int ew = w - w % 2, eh = h - h % 2;
        //rows, cols - number of rows and cols in the image
        int rows = eh / ss + 1;
        int cols = ew / ss + 1;
        //make rows and cols odd
        if (!(rows % 2)) {
            rows++;
        }
        if (!(cols % 2)) {
            cols++;
        }
        
        //calculate limits
        int level = root->level();
        long min, max;
        if (level > 63) {
            min = LONG_MIN;
            max = LONG_MAX;
        } else {
            min = -powl(2, level - 1);
            max = powl(2, level - 1) - 1;
        }
        
        //edge rows and cols
        long r0 = cy - rows / 2;
        long r1 = cy + rows / 2;
        long c0 = cx - cols / 2;
        long c1 = cx + cols / 2;
        
        //corner flags: NW, NE, SW, SE
        uchar flags = 0xf;
        uchar NW = 0x8, NE = 0x4, SW = 0x2, SE = 0x1;
        if (r0 < min) {
            flags &= ~(SW | SE); //0xc
            r0 = min - 1; //since center starts from r0 + 1
        }
        if (r1 > max) {
            flags &= ~(NW | NE); //0x3
            r1 = max + 1; //since center ends at r1
        }
        if (c0 < min) {
            flags &= ~(NW | SW); //0x5
            c0 = min - 1;
        }
        if (c1 > max) {
            flags &= ~(NE | SE); //0xa
            c1 = max + 1;
        }
        
        //image center
        int icx = ew / 2, icy = eh / 2;
        //half side
        int hs = ss / 2;
        //inner square bounds
        long ix0 = icx - hs - ss * (cx - c0 - 1);
        long iy0 = icy - hs - ss * (cy - r0 - 1);
        long ix1 = icx + hs + ss * (c1 - cx - 1);
        long iy1 = icy + hs + ss * (r1 - cy - 1);
        
        //corners
        if (flags & NW) {
            if (get_cell(root, c0, r1)) {
                fill(pixels, w, 0, iy1, ix0, eh);
            }
        }
        if (flags & NE) {
            if (get_cell(root, c1, r1)) {
                fill(pixels, w, ix1, iy1, ew, eh);
            }
        }
        if (flags & SW) {
            if (get_cell(root, c0, r0)) {
                fill(pixels, w, 0, 0, ix0, iy0);
            }
        }
        if (flags & SE) {
            if (get_cell(root, c1, r0)) {
                fill(pixels, w, ix1, 0, ew, iy0);
            }
        }
        
        //edges - top, bottom, left, right
        if (flags & (NW | NE)) {
            for (long i = c0 + 1; i < c1; i++) {
                if (get_cell(root, i, r1)) {
                    rect(pixels, w, ix0 + ss * (i - c0 - 1), iy1, ss, eh - iy1);
                }
            }
        }
        if (flags & (SW | SE)) {
            for (long i = c0 + 1; i < c1; i++) {
                if (get_cell(root, i, r0)) {
                    rect(pixels, w, ix0 + ss * (i - c0 - 1), 0, ss, iy0);
                }
            }
        }
        if (flags & (NW | SW)) {
            for (long i = r0 + 1; i < r1; i++) {
                if (get_cell(root, c0, i)) {
                    rect(pixels, w, 0, iy0 + ss * (i - r0 - 1), ix0, ss);
                }
            }
        }
        if (flags & (NE | SE)) {
            for (long i = r0 + 1; i < r1; i++) {
                if (get_cell(root, c1, i)) {
                    rect(pixels, w, ix1, iy0 + ss * (i - r0 - 1), ew - ix1, ss);
                }
            }
        }
        
        //inner square
        for (long y = r0 + 1; y < r1; y++) {
            for (long x = c0 + 1; x < c1; x++) {
                if (get_cell(root, x, y)) {
                    rect(pixels, w, ix0 + ss * (x - c0 - 1), iy0 + ss * (y - r0 - 1), ss, ss);
                }
            }
        }
    }
}
