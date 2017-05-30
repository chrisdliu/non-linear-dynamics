//
//  hashlife.h
//  hashlife
//
//  Created by Chris Liu on 4/9/17.
//  Copyright © 2017 Chris Liu. All rights reserved.
//

#ifndef hashlife_h
#define hashlife_h

#include <stdio.h>
#include <chrono>

typedef unsigned char uchar;
typedef unsigned int uint;
typedef unsigned long ulong;

long last = 0;
long mark() {
    using namespace std::chrono;
    long now = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
    long diff = now - last;
    last = now;
    return diff;
}

class Node;
class Future;
class HashTable;

class Node {
public:
    //members
    
    //hash chain
    Node* next;
    
    //quadtree
    //0 when base case (1x1)
    Node* nw;
    Node* ne;
    Node* sw;
    Node* se;
    
    //pop
    long pop;
    
    //futures
    //Node* future;
    Future* future;
    
    //functions
    Node(Node* nw, Node* ne, Node* sw, Node* se);
    ~Node();
    
    bool alive();
    int level();
    bool contains(Node* node);
    Node* expand(HashTable* hashtable);
    Node* compact(HashTable* hashtable);
    Node* turn(HashTable* hashtable, int power);
    void add_future(Node* node, int power);
    Node* get_future(int power);
    
    static Node* center(HashTable* hashtable, Node* node);
    static Node* horizontal(HashTable* hashtable, Node* left, Node* right);
    static Node* vertical(HashTable* hashtable, Node* up, Node* down);
    static Node* horizontal_center(HashTable* hashtable, Node* left, Node* right);
    static Node* vertical_center(HashTable* hashtable, Node* up, Node* down);
    
    //store all level 0-2 nodes to stop recursion
    static Node** LVL0;
    static Node** LVL1;
    static Node** LVL2;
    
    static uint hash(Node* nw, Node* ne, Node* sw, Node* se);
    static void set_base_nodes(int bflags, int sflags);
    static void delete_base_nodes();
    static Node* zero_node(HashTable* hashtable, int level);
};

Node** Node::LVL0;
Node** Node::LVL1;
Node** Node::LVL2;

class Future {
public:
    Node* node;
    int power;
    Future* next;
    
    Future(Node* node, int power);
    ~Future();
};

class HashTable {
public:
    //members
    Node** table;
    int hashprime;
    int hashcount;
    
    //functions
    HashTable();
    ~HashTable();
    void clear();
    void clean(Node* root);
    
    void add(Node* node);
    Node* get(Node* nw, Node* ne, Node* sw, Node* se);
    
    void report();
    
    static void add_base_nodes(HashTable* hashtable);
};

#endif /* hashlife_h */
