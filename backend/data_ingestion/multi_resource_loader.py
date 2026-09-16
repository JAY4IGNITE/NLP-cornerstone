"""Multi-Resource Academic Dataset Ingestion Engine for Cloudflare Vectorize.
Builds and ingests a comprehensive university student knowledge base from:
1. Official B.Tech Computer Science Curriculum & Syllabi (CS201 - CS414)
2. Academic Regulations, Exam Rules & 10-Point Grading Scheme
3. Campus Services, Hostel Life, Library, Scholarships & Placement FAQs
4. Core CS Subject Study Guides & High-Yield Revision Cheat Sheets
5. Academic Calendar, Important Dates & Examination Milestones
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Any

from backend.config import BASE_DIR, DATA_DIR, DOCUMENTS_DIR, settings
from backend.rag.embeddings import embedding_service
from backend.rag.cloudflare_vector_store import cloudflare_vector_store
from backend.utils.logger import logger

RESOURCES_DIR = BASE_DIR / "documents"
CURRICULUM_DIR = RESOURCES_DIR / "curriculum"
REGULATIONS_DIR = RESOURCES_DIR / "regulations"
CAMPUS_DIR = RESOURCES_DIR / "campus_services"
STUDY_GUIDES_DIR = RESOURCES_DIR / "study_guides"
CALENDAR_DIR = RESOURCES_DIR / "academic_calendar"

for d in [CURRICULUM_DIR, REGULATIONS_DIR, CAMPUS_DIR, STUDY_GUIDES_DIR, CALENDAR_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# RESOURCE 1: COMPREHENSIVE CURRICULUM & ELECTIVES SYLLABI
# -------------------------------------------------------------
CURRICULUM_RECORDS = [
    # CS201
    {
        "chunk_id": "cs201_meta",
        "category": "curriculum",
        "course_code": "CS201",
        "course_name": "Data Structures and Algorithms",
        "branch": "CSE",
        "semester": 3,
        "credits": 4,
        "ltp": "3-1-0",
        "prerequisites": "Programming for Problem Solving (CS101)",
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 2,
        "section_heading": "Course Overview & Prerequisites",
        "text": """Course: DATA STRUCTURES AND ALGORITHMS (CS201)
Credits: 4.0 (L: 3, T: 1, P: 0) | Semester: 3 | Branch: CSE
Prerequisites: CS101 Programming for Problem Solving (C / Python).
Course Objectives:
- Master linear and non-linear abstract data types: arrays, stacks, queues, linked lists, trees, and graphs.
- Analyze algorithmic asymptotic time and space complexity using Big-O, Omega, and Theta notations.
- Formulate recursive problem solving, divide-and-conquer, greedy techniques, and dynamic programming."""
    },
    {
        "chunk_id": "cs201_u1",
        "category": "curriculum",
        "course_code": "CS201",
        "course_name": "Data Structures and Algorithms",
        "branch": "CSE",
        "semester": 3,
        "unit": 1,
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 2,
        "section_heading": "Unit 1: Linear Data Structures & Analysis",
        "text": """Course: DATA STRUCTURES AND ALGORITHMS (CS201)
Section: Unit 1 - Linear Data Structures & Asymptotic Analysis
Topics Covered:
Asymptotic notation: Big-O, Big-Omega, Big-Theta, Little-o notations; Master theorem for divide-and-conquer recurrences.
Arrays: Row-major and Column-major order representations, sparse matrices.
Singly linked lists, Doubly linked lists, Circular linked lists, polynomial addition using linked lists.
Stacks: Array and linked implementations, applications: infix to postfix conversion, postfix expression evaluation, parenthesis validation.
Queues: FIFO queues, Circular queues, Double-Ended Queues (Deque), Priority Queues."""
    },
    {
        "chunk_id": "cs201_u2",
        "category": "curriculum",
        "course_code": "CS201",
        "course_name": "Data Structures and Algorithms",
        "branch": "CSE",
        "semester": 3,
        "unit": 2,
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 2,
        "section_heading": "Unit 2: Trees & Balanced Search Trees",
        "text": """Course: DATA STRUCTURES AND ALGORITHMS (CS201)
Section: Unit 2 - Trees & Search Structures
Topics Covered:
Trees terminology: degree, height, depth. Binary trees, full and complete binary trees, array vs linked representations.
Tree Traversals: Preorder, Inorder, Postorder, and Level-Order traversals.
Binary Search Trees (BST): insertion, deletion, searching, in-order predecessor/successor.
Balanced Search Trees: AVL trees (single and double rotations: LL, RR, LR, RL), Red-Black Trees properties.
B-Trees and B+ Trees: multi-way search trees for disk storage indexing."""
    },
    {
        "chunk_id": "cs201_u3",
        "category": "curriculum",
        "course_code": "CS201",
        "course_name": "Data Structures and Algorithms",
        "branch": "CSE",
        "semester": 3,
        "unit": 3,
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 2,
        "section_heading": "Unit 3: Graphs & Shortest Path Algorithms",
        "text": """Course: DATA STRUCTURES AND ALGORITHMS (CS201)
Section: Unit 3 - Graph Algorithms
Topics Covered:
Graph representations: Adjacency Matrix and Adjacency List.
Graph Traversals: Breadth-First Search (BFS) using queues, Depth-First Search (DFS) using recursion/stacks.
Topological Sorting for Directed Acyclic Graphs (DAGs).
Minimum Spanning Trees: Prim's algorithm and Kruskal's algorithm with Disjoint-Set Union (Union-Find).
Shortest Path Algorithms: Dijkstra's single-source shortest path, Bellman-Ford for negative weights, Floyd-Warshall all-pairs shortest paths."""
    },
    {
        "chunk_id": "cs201_u4",
        "category": "curriculum",
        "course_code": "CS201",
        "course_name": "Data Structures and Algorithms",
        "branch": "CSE",
        "semester": 3,
        "unit": 4,
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 2,
        "section_heading": "Unit 4: Sorting, Searching & Hashing",
        "text": """Course: DATA STRUCTURES AND ALGORITHMS (CS201)
Section: Unit 4 - Sorting, Searching and Hashing
Topics Covered:
Searching: Linear Search, Binary Search, Interpolation Search.
Sorting Algorithms: Bubble Sort, Selection Sort, Insertion Sort (O(N^2)); Merge Sort, Quick Sort (average O(N log N)); Heap Sort; Non-comparison sorting: Counting Sort, Radix Sort.
Hashing: Hash functions (division, multiplication, mid-square), Collision resolution: Separate Chaining, Open Addressing (Linear Probing, Quadratic Probing, Double Hashing)."""
    },
    {
        "chunk_id": "cs201_u5",
        "category": "curriculum",
        "course_code": "CS201",
        "course_name": "Data Structures and Algorithms",
        "branch": "CSE",
        "semester": 3,
        "unit": 5,
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 2,
        "section_heading": "Unit 5: Advanced Algorithmic Paradigms",
        "text": """Course: DATA STRUCTURES AND ALGORITHMS (CS201)
Section: Unit 5 - Algorithm Design Strategies
Topics Covered:
Greedy Method: Fractional Knapsack, Huffman coding, Job sequencing with deadlines.
Dynamic Programming: 0/1 Knapsack problem, Longest Common Subsequence (LCS), Matrix Chain Multiplication, Floyd-Warshall.
Backtracking: N-Queens problem, Subset Sum problem, Hamiltonian Cycle.
Branch and Bound: Traveling Salesperson Problem (TSP)."""
    },

    # CS301 DBMS
    {
        "chunk_id": "cs301_meta",
        "category": "curriculum",
        "course_code": "CS301",
        "course_name": "Database Management Systems",
        "branch": "CSE",
        "semester": 5,
        "credits": 4,
        "ltp": "3-1-0",
        "prerequisites": "Data Structures and Algorithms (CS201)",
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 3,
        "section_heading": "Course Overview & Prerequisites",
        "text": """Course: DATABASE MANAGEMENT SYSTEMS (CS301)
Credits: 4.0 (L: 3, T: 1, P: 0) | Semester: 5 | Branch: CSE
Prerequisites: CS201 Data Structures and Algorithms.
Course Objectives:
- Master relational database design principles, Entity-Relationship (ER) modeling, and Relational Algebra.
- Develop complex declarative queries using Structured Query Language (SQL) including joins, subqueries, triggers, and views.
- Understand transaction management: ACID properties, concurrency control mechanisms, and crash recovery techniques.
- Apply database normalization up to Boyce-Codd Normal Form (BCNF) to eliminate data redundancy."""
    },
    {
        "chunk_id": "cs301_u1",
        "category": "curriculum",
        "course_code": "CS301",
        "course_name": "Database Management Systems",
        "branch": "CSE",
        "semester": 5,
        "unit": 1,
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 3,
        "section_heading": "Unit 1: ER Modeling & Relational Algebra",
        "text": """Course: DATABASE MANAGEMENT SYSTEMS (CS301)
Section: Unit 1 - Database System Concepts & ER Model
Topics Covered:
Database System Architecture: 3-tier ANSI-SPARC schema architecture, physical vs logical data independence.
Entity-Relationship (ER) model: Entities, attributes, entity sets, relationships, cardinalities, weak entities, ER diagrams to relational schema mapping.
Relational Algebra: Selection, Projection, Union, Set Difference, Cartesian Product, Rename, Natural Join, Outer Joins, Division operator."""
    },
    {
        "chunk_id": "cs301_u2",
        "category": "curriculum",
        "course_code": "CS301",
        "course_name": "Database Management Systems",
        "branch": "CSE",
        "semester": 5,
        "unit": 2,
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 3,
        "section_heading": "Unit 2: SQL, DDL, DML & Triggers",
        "text": """Course: DATABASE MANAGEMENT SYSTEMS (CS301)
Section: Unit 2 - Structured Query Language (SQL)
Topics Covered:
Data Definition Language (DDL): CREATE, ALTER, DROP, TRUNCATE, primary key, foreign key, unique, check constraints.
Data Manipulation Language (DML): INSERT, UPDATE, DELETE, SELECT with WHERE, GROUP BY, HAVING, ORDER BY.
Joins: Inner Join, Left/Right/Full Outer Joins, Self Join. Nested correlated subqueries.
Views, Indexes, Stored Procedures, and Event Triggers."""
    },
    {
        "chunk_id": "cs301_u3",
        "category": "curriculum",
        "course_code": "CS301",
        "course_name": "Database Management Systems",
        "branch": "CSE",
        "semester": 5,
        "unit": 3,
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 3,
        "section_heading": "Unit 3: Relational Design & Normalization",
        "text": """Course: DATABASE MANAGEMENT SYSTEMS (CS301)
Section: Unit 3 - Normalization & Schema Refinement
Topics Covered:
Functional Dependencies (FD): Armstrong's Axioms, closure of functional dependencies, minimal cover of FDs.
Anomalies: Insertion, deletion, and update anomalies in unnormalized schemas.
Normal Forms: First Normal Form (1NF - atomic values), Second Normal Form (2NF - elimination of partial functional dependencies), Third Normal Form (3NF - elimination of transitive dependencies), Boyce-Codd Normal Form (BCNF - every determinant is a candidate key).
Lossless-join decomposition and Dependency preservation properties."""
    },
    {
        "chunk_id": "cs301_u4",
        "category": "curriculum",
        "course_code": "CS301",
        "course_name": "Database Management Systems",
        "branch": "CSE",
        "semester": 5,
        "unit": 4,
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 3,
        "section_heading": "Unit 4: Transactions & Concurrency Control",
        "text": """Course: DATABASE MANAGEMENT SYSTEMS (CS301)
Section: Unit 4 - Transaction Management & Concurrency
Topics Covered:
ACID Properties: Atomicity, Consistency, Isolation, Durability.
Transaction states: Active, Partially Committed, Committed, Failed, Aborted.
Concurrent Executions: Serializability, Conflict Serializability, Precedence Graph (Serialization Graph), View Serializability.
Concurrency Control Protocols: Lock-Based Protocols: Shared (S) and Exclusive (X) locks, Two-Phase Locking (2PL), Strict 2PL, Rigorous 2PL; Deadlock detection, prevention, and recovery (Wait-Die, Wound-Wait).
Timestamp-Based Protocols: Thomas Write Rule."""
    },
    {
        "chunk_id": "cs301_u5",
        "category": "curriculum",
        "course_code": "CS301",
        "course_name": "Database Management Systems",
        "branch": "CSE",
        "semester": 5,
        "unit": 5,
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 3,
        "section_heading": "Unit 5: Crash Recovery & Indexing",
        "text": """Course: DATABASE MANAGEMENT SYSTEMS (CS301)
Section: Unit 5 - Recovery & Storage Organization
Topics Covered:
Storage Hierarchy: Primary, secondary, tertiary storage; File organization: Heap files, Sorted files, Hashing.
Indexing: Dense vs Sparse indexes, Primary vs Secondary indexes, Multi-level indexing, B+ Tree index insertion and deletion.
Crash Recovery: Log-based recovery, Write-Ahead Logging (WAL) protocol, Deferred database modification, Immediate database modification, Checkpointing; ARIES recovery algorithm."""
    },

    # CS302 Operating Systems
    {
        "chunk_id": "cs302_meta",
        "category": "curriculum",
        "course_code": "CS302",
        "course_name": "Operating Systems",
        "branch": "CSE",
        "semester": 5,
        "credits": 4,
        "ltp": "3-1-0",
        "prerequisites": "Computer Organization & Architecture (CS203), Data Structures (CS201)",
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 4,
        "section_heading": "Course Overview & Prerequisites",
        "text": """Course: OPERATING SYSTEMS (CS302)
Credits: 4.0 (L: 3, T: 1, P: 0) | Semester: 5 | Branch: CSE
Prerequisites: CS203 Computer Organization & Architecture, CS201 Data Structures and Algorithms.
Course Objectives:
- Study OS architecture: dual-mode execution (user vs kernel mode), system calls, interrupts.
- Analyze CPU scheduling algorithms, process synchronization, and deadlock prevention.
- Explore memory management: paging, virtual memory, page replacement algorithms.
- Understand file system implementation, mass storage management, and disk scheduling."""
    },
    {
        "chunk_id": "cs302_u1",
        "category": "curriculum",
        "course_code": "CS302",
        "course_name": "Operating Systems",
        "branch": "CSE",
        "semester": 5,
        "unit": 1,
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 4,
        "section_heading": "Unit 1: Process Management & CPU Scheduling",
        "text": """Course: OPERATING SYSTEMS (CS302)
Section: Unit 1 - Processes & CPU Scheduling
Topics Covered:
Process Concept: Process Control Block (PCB), process states (New, Ready, Running, Waiting, Terminated).
Context Switching, Process scheduling queues, Inter-Process Communication (IPC): Shared memory and Message passing.
Threads: Kernel-level vs User-level threads, Multithreading models (Many-to-One, One-to-One, Many-to-Many).
CPU Scheduling: Preemptive vs Non-preemptive scheduling; Scheduling algorithms: First-Come First-Served (FCFS), Shortest Job First (SJF), Shortest Remaining Time First (SRTF), Priority Scheduling, Round Robin (RR) with time quantum, Multilevel Queue Scheduling, Multilevel Feedback Queue Scheduling."""
    },
    {
        "chunk_id": "cs302_u2",
        "category": "curriculum",
        "course_code": "CS302",
        "course_name": "Operating Systems",
        "branch": "CSE",
        "semester": 5,
        "unit": 2,
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 4,
        "section_heading": "Unit 2: Process Synchronization & Deadlocks",
        "text": """Course: OPERATING SYSTEMS (CS302)
Section: Unit 2 - Concurrency & Deadlocks
Topics Covered:
Critical Section Problem: Mutual Exclusion, Progress, Bounded Waiting conditions.
Software solutions: Peterson's algorithm; Hardware support: Test-and-Set, Compare-and-Swap instructions.
Semaphores: Counting and Binary (mutex) semaphores, wait() and signal() primitives.
Classical Synchronization Problems: Producer-Consumer problem with bounded buffer, Readers-Writers problem, Dining Philosophers problem.
Deadlocks: 4 Necessary conditions (Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait); Resource Allocation Graph (RAG); Deadlock Prevention; Deadlock Avoidance: Banker's Algorithm; Deadlock Detection and Recovery."""
    },
    {
        "chunk_id": "cs302_u3",
        "category": "curriculum",
        "course_code": "CS302",
        "course_name": "Operating Systems",
        "branch": "CSE",
        "semester": 5,
        "unit": 3,
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 4,
        "section_heading": "Unit 3: Main Memory & Virtual Memory",
        "text": """Course: OPERATING SYSTEMS (CS302)
Section: Unit 3 - Memory Management & Virtual Memory
Topics Covered:
Memory management hardware: Base and Limit registers, Logical vs Physical address space, Memory Management Unit (MMU).
Contiguous Memory Allocation: Fixed vs Dynamic partitioning, First-Fit, Best-Fit, Worst-Fit allocation; Internal and External Fragmentation; Compaction.
Paging: Page table architecture, Translation Lookaside Buffer (TLB), effective memory access time (EMAT), Hierarchical paging, Inverted page tables. Segmentation.
Virtual Memory: Demand Paging, Page Fault handling routine; Page Replacement Algorithms: FIFO, Belady's Anomaly, Optimal Page Replacement (OPT), Least Recently Used (LRU), Second-Chance (Clock) algorithm; Thrashing, Working Set Model."""
    },

    # CS303 Computer Networks
    {
        "chunk_id": "cs303_meta",
        "category": "curriculum",
        "course_code": "CS303",
        "course_name": "Computer Networks",
        "branch": "CSE",
        "semester": 5,
        "credits": 3,
        "ltp": "3-0-0",
        "prerequisites": "Data Structures (CS201)",
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 4,
        "section_heading": "Course Overview & Prerequisites",
        "text": """Course: COMPUTER NETWORKS (CS303)
Credits: 3.0 (L: 3, T: 0, P: 0) | Semester: 5 | Branch: CSE
Prerequisites: CS201 Data Structures and Algorithms.
Course Objectives:
- Master ISO-OSI 7-layer reference model and TCP/IP protocol suite.
- Understand data link layer framing, error detection (CRC, Hamming code), and flow control.
- Analyze network layer IP addressing, CIDR subnetting, and intra/inter-domain routing protocols.
- Learn transport layer TCP/UDP mechanics, flow control, and congestion control."""
    },
    {
        "chunk_id": "cs303_u3",
        "category": "curriculum",
        "course_code": "CS303",
        "course_name": "Computer Networks",
        "branch": "CSE",
        "semester": 5,
        "unit": 3,
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 4,
        "section_heading": "Unit 3: Network Layer & Routing Protocols",
        "text": """Course: COMPUTER NETWORKS (CS303)
Section: Unit 3 - Network Layer & Routing
Topics Covered:
IPv4 Addressing: Classful addressing, Classless Inter-Domain Routing (CIDR), Subnetting and Supernetting calculations, Variable Length Subnet Masking (VLSM).
IPv4 Packet Header format, Fragmentation and Reassembly. IPv6 packet format and advantages over IPv4.
Address Resolution Protocol (ARP), Reverse ARP (RARP), Dynamic Host Configuration Protocol (DHCP), Internet Control Message Protocol (ICMP).
Routing Algorithms: Distance Vector Routing (Bellman-Ford, Count-to-Infinity problem, Split Horizon), Link State Routing (Dijkstra's algorithm, OSPF), Border Gateway Protocol (BGP)."""
    },

    # CS304 Compiler Design
    {
        "chunk_id": "cs304_meta",
        "category": "curriculum",
        "course_code": "CS304",
        "course_name": "Compiler Design",
        "branch": "CSE",
        "semester": 6,
        "credits": 4,
        "ltp": "3-1-0",
        "prerequisites": "Formal Languages and Automata Theory (CS205), Data Structures (CS201)",
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 5,
        "section_heading": "Course Overview & Prerequisites",
        "text": """Course: COMPILER DESIGN (CS304)
Credits: 4.0 (L: 3, T: 1, P: 0) | Semester: 6 | Branch: CSE
Prerequisites: CS205 Formal Languages and Automata Theory, CS201 Data Structures and Algorithms.
Course Objectives:
- Study all phases of a modern language compiler: Lexical Analysis, Syntax Analysis, Semantic Analysis, Intermediate Code Generation, Code Optimization, Target Code Generation.
- Implement Lexical Analyzers with Lex/Flex and Parsers with Yacc/Bison.
- Master Top-Down (LL(1)) and Bottom-Up (LR(0), SLR(1), CLR(1), LALR(1)) parsing.
- Apply Syntax-Directed Translation (SDT), Three-Address Code generation, and DAG optimizations."""
    },

    # CS401 Machine Learning
    {
        "chunk_id": "cs401_meta",
        "category": "curriculum",
        "course_code": "CS401",
        "course_name": "Machine Learning",
        "branch": "CSE",
        "semester": 7,
        "credits": 4,
        "ltp": "3-1-0",
        "prerequisites": "Linear Algebra, Probability & Statistics, Python Programming",
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 8,
        "section_heading": "Course Overview & Prerequisites",
        "text": """Course: MACHINE LEARNING (CS401)
Credits: 4.0 (L: 3, T: 1, P: 0) | Semester: 7 | Branch: CSE
Prerequisites: Linear Algebra, Multivariate Calculus, Probability & Statistics, Python.
Course Objectives:
- Understand foundational machine learning algorithms: Linear Regression, Logistic Regression, Decision Trees, Random Forests, Support Vector Machines (SVM).
- Master dimensionality reduction: Principal Component Analysis (PCA), Linear Discriminant Analysis (LDA).
- Explore unsupervised clustering: K-Means, Hierarchical Clustering, DBSCAN.
- Learn deep learning fundamentals: Multilayer Perceptrons (MLP), Backpropagation, Gradient Descent variants."""
    },

    # CS402 Artificial Intelligence
    {
        "chunk_id": "cs402_meta",
        "category": "curriculum",
        "course_code": "CS402",
        "course_name": "Artificial Intelligence",
        "branch": "CSE",
        "semester": 7,
        "credits": 3,
        "ltp": "3-0-0",
        "prerequisites": "Data Structures & Algorithms (CS201), Discrete Mathematics",
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 9,
        "section_heading": "Course Overview & Prerequisites",
        "text": """Course: ARTIFICIAL INTELLIGENCE (CS402)
Credits: 3.0 (L: 3, T: 0, P: 0) | Semester: 7 | Branch: CSE
Prerequisites: CS201 Data Structures and Algorithms, Discrete Mathematics.
Course Objectives:
- Study intelligent agents: reflex, goal-based, utility-based agents and state space search.
- Master heuristic search techniques: Greedy Best-First Search, A* search, IDA*, Adversarial Search (Minimax, Alpha-Beta pruning).
- Explore knowledge representation: Propositional Logic, First-Order Logic (FOL), resolution refutation.
- Study probabilistic reasoning: Bayesian Networks and Markov Decision Processes (MDPs)."""
    },

    # CS403 Cloud Computing
    {
        "chunk_id": "cs403_meta",
        "category": "curriculum",
        "course_code": "CS403",
        "course_name": "Cloud Computing",
        "branch": "CSE",
        "semester": 8,
        "credits": 3,
        "ltp": "3-0-0",
        "prerequisites": "Operating Systems (CS302), Computer Networks (CS303)",
        "source_document": "CSE_Curriculum_2025.pdf",
        "page_number": 11,
        "section_heading": "Course Overview & Prerequisites",
        "text": """Course: CLOUD COMPUTING (CS403)
Credits: 3.0 (L: 3, T: 0, P: 0) | Semester: 8 | Branch: CSE
Prerequisites: CS302 Operating Systems, CS303 Computer Networks.
Course Objectives:
- Understand cloud service models: IaaS, PaaS, SaaS, and deployment models: Public, Private, Hybrid, Community.
- Explore hardware virtualization: Type-1 (bare-metal) vs Type-2 hypervisors, containers (Docker, Kubernetes).
- Analyze cloud storage architectures: Object storage (S3), Block storage (EBS), Distributed file systems.
- Master serverless computing, cloud elasticity, auto-scaling, and cloud security frameworks."""
    }
]

# -------------------------------------------------------------
# RESOURCE 2: ACADEMIC REGULATIONS, ATTENDANCE & GRADING SCHEME
# -------------------------------------------------------------
REGULATION_RECORDS = [
    {
        "chunk_id": "reg_attendance_75",
        "category": "regulations",
        "course_code": "",
        "course_name": "Academic Regulations",
        "branch": "All Engineering",
        "semester": None,
        "source_document": "Academic_Regulations_2025.pdf",
        "page_number": 1,
        "section_heading": "Clause 4.1: Mandatory 75% Attendance Requirement",
        "text": """OFFICIAL ACADEMIC REGULATIONS: ATTENDANCE MANDATE (Clause 4.1)
1. Every registered student is required to attend 100% of the lectures, practicals, and tutorial sessions.
2. A minimum aggregate attendance of 75% across all registered subjects in the current semester is mandatory to qualify to appear for the End-Semester Examinations (ESE).
3. Attendance is computed from the date of commencement of the semester until the official last instructional working day.
4. Continuous biometric / RFID card attendance logging is recorded each period."""
    },
    {
        "chunk_id": "reg_condonation_medical",
        "category": "regulations",
        "course_code": "",
        "course_name": "Academic Regulations",
        "branch": "All Engineering",
        "semester": None,
        "source_document": "Academic_Regulations_2025.pdf",
        "page_number": 1,
        "section_heading": "Clause 4.2: Condonation of Attendance Shortage",
        "text": """OFFICIAL ACADEMIC REGULATIONS: CONDONATION OF SHORTAGE (Clause 4.2)
1. Condonation of attendance shortage between 65% and 74% may be recommended by the Department Head and approved by the Academic Council.
2. Condonation is granted strictly on valid grounds:
   - Genuine medical hospitalization or serious illness supported by authorized hospital discharge summary and medical certificate submitted within 3 days of resuming classes.
   - Official participation in inter-university sports tournaments, NCC/NSS state camps, or technical symposiums with prior Dean approval.
3. A prescribed condonation fee of Rs. 1,000 per subject must be paid prior to hall ticket generation.
4. Under NO circumstances shall attendance below 65% be condoned."""
    },
    {
        "chunk_id": "reg_detention_rules",
        "category": "regulations",
        "course_code": "",
        "course_name": "Academic Regulations",
        "branch": "All Engineering",
        "semester": None,
        "source_document": "Academic_Regulations_2025.pdf",
        "page_number": 2,
        "section_heading": "Clause 4.3: Semester Detention Policy",
        "text": """OFFICIAL ACADEMIC REGULATIONS: DETENTION POLICY (Clause 4.3)
1. A student securing less than 65% aggregate attendance in a semester is summarily DETAINED.
2. Detained students are strictly barred from appearing in the End Semester Examinations for all registered courses of that semester.
3. The student shall not be promoted to the subsequent semester and must seek re-admission to the same semester in the next academic year upon fee payment."""
    },
    {
        "chunk_id": "reg_exam_scheme_cia_ese",
        "category": "regulations",
        "course_code": "",
        "course_name": "Academic Regulations",
        "branch": "All Engineering",
        "semester": None,
        "source_document": "Academic_Regulations_2025.pdf",
        "page_number": 3,
        "section_heading": "Clause 5.1: Assessment Scheme (40% CIA + 60% ESE)",
        "text": """OFFICIAL ACADEMIC REGULATIONS: EXAMINATION EVALUATION PATTERN (Clause 5.1)
Theory Courses Evaluation:
1. Continuous Internal Assessment (CIA) - 40% Weightage (40 Marks):
   - Mid-Term Examination 1 (20 Marks) conducted after 7 weeks of instruction.
   - Mid-Term Examination 2 (20 Marks) conducted after 14 weeks of instruction.
   - Continuous Assignments, Quizzes & Class Presentations (10 Marks).
   - Internal mark is computed as: Best of Mid 1 or Mid 2 (15 Marks) + Average of Mid 1 & Mid 2 (15 Marks) + Assignments (10 Marks) = Total 40 Marks.
2. End-Semester Examination (ESE) - 60% Weightage (60 Marks):
   - 3-Hour comprehensive written examination conducted by University Examination Controller covering all 5 syllabus units.
Passing Standard:
- Minimum 40% marks (24 out of 60) required in the End-Semester Examination.
- Minimum 40% marks in aggregate (CIA + ESE combined, i.e., 40 out of 100)."""
    },
    {
        "chunk_id": "reg_grading_system_10pt",
        "category": "regulations",
        "course_code": "",
        "course_name": "Academic Regulations",
        "branch": "All Engineering",
        "semester": None,
        "source_document": "Academic_Regulations_2025.pdf",
        "page_number": 4,
        "section_heading": "Clause 6.1: 10-Point Letter Grading Scale",
        "text": """OFFICIAL ACADEMIC REGULATIONS: 10-POINT LETTER GRADING SYSTEM (Clause 6.1)
Standardized UGC/AICTE Letter Grade Scale:
- Grade 'O' (Outstanding): 90% - 100% | Grade Point: 10.0
- Grade 'A+' (Excellent): 80% - 89% | Grade Point: 9.0
- Grade 'A' (Very Good): 70% - 79% | Grade Point: 8.0
- Grade 'B+' (Good): 60% - 69% | Grade Point: 7.0
- Grade 'B' (Above Average): 55% - 59% | Grade Point: 6.0
- Grade 'C' (Average): 50% - 54% | Grade Point: 5.0
- Grade 'P' (Pass): 40% - 49% | Grade Point: 4.0
- Grade 'F' (Fail): Below 40% | Grade Point: 0.0
- Grade 'Ab' (Absent): Examination Not Taken | Grade Point: 0.0
Calculation of SGPA (Semester Grade Point Average):
SGPA = Sum(C_i * G_i) / Sum(C_i), where C_i is Course Credits and G_i is Grade Points earned in Course i.
Calculation of CGPA (Cumulative Grade Point Average):
CGPA = Sum of (C_i * G_i) across all passed semesters / Total Credits registered across all semesters."""
    },
    {
        "chunk_id": "reg_degree_160_credits",
        "category": "regulations",
        "course_code": "",
        "course_name": "Academic Regulations",
        "branch": "All Engineering",
        "semester": None,
        "source_document": "Academic_Regulations_2025.pdf",
        "page_number": 5,
        "section_heading": "Clause 7.1: B.Tech Degree Award Criteria",
        "text": """OFFICIAL ACADEMIC REGULATIONS: DEGREE AWARD CRITERIA (Clause 7.1)
A student is declared eligible for the award of Bachelor of Technology (B.Tech) Degree in Computer Science & Engineering provided:
1. The student has successfully earned 160 required academic credits across 8 semesters.
2. The student has achieved a final Cumulative Grade Point Average (CGPA) of at least 5.00.
3. The student has zero outstanding backlogs / arrears in any course.
4. The student has completed a mandatory 6-week industrial internship with approved corporate evaluation.
5. No disciplinary actions, malpractice penalties, or financial dues are pending against the student."""
    }
]

# -------------------------------------------------------------
# RESOURCE 3: CAMPUS LIFE, HOSTEL, LIBRARY & STUDENT SERVICES
# -------------------------------------------------------------
CAMPUS_SERVICES_RECORDS = [
    {
        "chunk_id": "campus_hostel_rules",
        "category": "campus_services",
        "course_code": "",
        "course_name": "Campus Student Services",
        "branch": "All",
        "semester": None,
        "source_document": "Campus_Life_Handbook_2025.pdf",
        "page_number": 1,
        "section_heading": "Hostel Admission & Residence Guidelines",
        "text": """CAMPUS RESIDENCE & HOSTEL REGULATIONS
Hostel Curfew & Timings:
- Main hostel gates close strictly at 9:30 PM on weekdays and 10:00 PM on weekends.
- Biometric attendance is taken between 9:30 PM and 10:15 PM daily by resident wardens.
- Night Leave & Outstation Pass: Students desiring to leave campus overnight must submit an online e-Leave request through the Student Portal endorsed by parents 24 hours in advance.
Mess Timings:
- Breakfast: 7:30 AM to 9:00 AM
- Lunch: 12:30 PM to 2:00 PM
- Evening Tea & Snacks: 5:00 PM to 6:00 PM
- Dinner: 7:30 PM to 9:30 PM
Prohibited Items: Immersion water heaters, induction cooktops, and personal refrigerators are strictly prohibited. Laundry facilities are operational on floors 1 and 3."""
    },
    {
        "chunk_id": "campus_library_services",
        "category": "campus_services",
        "course_code": "",
        "course_name": "Campus Student Services",
        "branch": "All",
        "semester": None,
        "source_document": "Campus_Life_Handbook_2025.pdf",
        "page_number": 2,
        "section_heading": "Central Library & Digital Academic Repositories",
        "text": """CENTRAL UNIVERSITY LIBRARY FACILITIES & BORROWING POLICIES
Library Working Hours:
- General Days: 8:00 AM to 10:00 PM
- Examination Periods (Mid-Terms & End-Semester): Open 24/7 with air-conditioned reading halls and Wi-Fi.
Borrowing Entitlement:
- Undergraduate B.Tech students are issued 4 RFID Library Borrower Cards.
- Books can be borrowed for 14 calendar days, renewable once online if no hold has been placed.
- Overdue Fine: Rs. 2 per day per volume after the grace return date.
Digital Resources & Electronic Subscriptions:
- Access to IEEE Xplore, ACM Digital Library, SpringerLink, ScienceDirect, and Scopus.
- Remote campus VPN credentials for home access are provisioned via university email @student.university.edu."""
    },
    {
        "chunk_id": "campus_scholarships_aid",
        "category": "campus_services",
        "course_code": "",
        "course_name": "Campus Student Services",
        "branch": "All",
        "semester": None,
        "source_document": "Campus_Life_Handbook_2025.pdf",
        "page_number": 3,
        "section_heading": "Scholarships, Fee Concessions & Financial Aid",
        "text": """STUDENT FINANCIAL AID & SCHOLARSHIPS SCHEMES
1. Merit Scholarship:
- Top 5% students in each branch based on annual CGPA (>= 9.0) receive a 50% tuition fee waiver for the succeeding academic year.
2. Merit-cum-Means Financial Assistance:
- Available for students with annual family income below Rs. 5,00,000. Up to 100% tuition waiver upon income certificate verification by the Welfare Office.
3. Government Scholarship Portals:
- Institutional verification for National Scholarship Portal (NSP), State Post-Matric SC/ST/OBC scholarships, and PMSSS schemes handled at Administrative Block Window 4.
- Application submission deadline for winter cycle: October 31 annually."""
    },
    {
        "chunk_id": "campus_placement_cell",
        "category": "campus_services",
        "course_code": "",
        "course_name": "Campus Student Services",
        "branch": "All",
        "semester": None,
        "source_document": "Campus_Life_Handbook_2025.pdf",
        "page_number": 4,
        "section_heading": "Training & Placement Cell (T&P) Policies",
        "text": """TRAINING & PLACEMENT CELL (T&P) GUIDELINES
Eligibility Criteria for Campus Recruitment:
- Minimum cumulative CGPA of 6.50 with no standing active backlogs at the time of recruitment drive registration.
- Minimum 80% attendance in mandatory pre-placement training modules (Aptitude, Coding, Soft Skills).
Offer Acceptance Policy:
- 'One Student, One Job' core policy: Once placed in a company offering CTC < Rs. 10 LPA, a student is eligible only for 'Dream Companies' offering CTC >= Rs. 12 LPA.
- Internship No Objection Certificate (NOC): 8th-semester full-semester internships are permitted for verified corporate offers with stipends >= Rs. 25,000/month."""
    },
    {
        "chunk_id": "campus_antiragging_safety",
        "category": "campus_services",
        "course_code": "",
        "course_name": "Campus Student Services",
        "branch": "All",
        "semester": None,
        "source_document": "Campus_Life_Handbook_2025.pdf",
        "page_number": 5,
        "section_heading": "Anti-Ragging Mandates & Student Health Clinic",
        "text": """CAMPUS SAFETY & EMERGENCY MEDICAL SERVICES
Anti-Ragging Zero Tolerance Policy:
- Ragging in any form (physical, verbal, online) is a cognizable criminal offense punishable under UGC Anti-Ragging Regulations.
- Penalties include immediate suspension, rustication, and filing of Police FIR.
- National Anti-Ragging 24x7 Helpline: 1800-180-5522 | Email: helpline@antiragging.in
- Campus Chief Proctor Helpline: +91-9876543210 (24x7 on-call).
Campus Health Center:
- 24/7 Outpatient dispensary staffed by resident medical officers and qualified nurses.
- Free basic pharmaceuticals, oxygen cylinders, first aid, and ambulance transfer service.
- Psychological Counseling & Mental Wellness Center: Open Monday to Friday, 9:00 AM to 5:00 PM (strictly confidential)."""
    }
]

# -------------------------------------------------------------
# RESOURCE 4: STUDY GUIDES & HIGH-YIELD REVISION CHEAT SHEETS
# -------------------------------------------------------------
STUDY_GUIDE_RECORDS = [
    {
        "chunk_id": "study_dsa_cheatsheet",
        "category": "study_guides",
        "course_code": "CS201",
        "course_name": "Data Structures & Algorithms",
        "branch": "CSE",
        "semester": 3,
        "source_document": "DSA_Quick_Revision_Notes.pdf",
        "page_number": 1,
        "section_heading": "DSA Time Complexities & Algorithm Summary",
        "text": """DATA STRUCTURES & ALGORITHMS HIGH-YIELD CHEAT SHEET
Algorithm Complexity Reference:
- Array Access: O(1) | Search: O(N) | Insertion/Deletion: O(N)
- Singly Linked List: Search O(N) | Insert/Delete at Head: O(1)
- Binary Search Tree (BST): Average Search/Insert/Delete O(log N) | Worst Case O(N) (skewed)
- AVL Tree / Red-Black Tree: Guaranteed Search/Insert/Delete O(log N) in worst case
- Hash Table: Average Search/Insert/Delete O(1) | Worst Case O(N) under high collisions
Sorting Complexities:
- Quick Sort: Best/Average O(N log N) | Worst Case O(N^2) | Space O(log N) | Not Stable
- Merge Sort: Best/Average/Worst O(N log N) | Space O(N) | Stable
- Heap Sort: Best/Average/Worst O(N log N) | Space O(1) | Not Stable
Graph Traversal:
- BFS: Uses Queue | Time O(V + E) | Finds unweighted shortest path
- DFS: Uses Stack / Recursion | Time O(V + E) | Finds connected components, cycles, topological sort
- Dijkstra: Greedy single-source shortest path | Time O((V + E) log V) with min-heap | Fails with negative edge weights!"""
    },
    {
        "chunk_id": "study_dbms_normalization_cheatsheet",
        "category": "study_guides",
        "course_code": "CS301",
        "course_name": "Database Management Systems",
        "branch": "CSE",
        "semester": 5,
        "source_document": "DBMS_Quick_Revision_Notes.pdf",
        "page_number": 1,
        "section_heading": "DBMS Normalization & ACID Properties Summary",
        "text": """DATABASE MANAGEMENT SYSTEMS HIGH-YIELD CHEAT SHEET
Database Normalization Quick Rules:
1. 1NF (First Normal Form): All attributes must hold single, atomic values. No repeating groups or multi-valued columns.
2. 2NF (Second Normal Form): Table is in 1NF AND no non-prime attribute is partially dependent on any candidate key (requires composite key to violate).
3. 3NF (Third Normal Form): Table is in 2NF AND no non-prime attribute is transitively dependent on candidate keys (For every X -> Y, either X is a superkey or Y is prime).
4. BCNF (Boyce-Codd Normal Form): Strictest form of 3NF. For every non-trivial functional dependency X -> Y, X MUST be a Superkey!
Transaction ACID Rules:
- Atomicity: All-or-nothing execution guaranteed via Undo logging.
- Consistency: Preserves database integrity constraints before and after commit.
- Isolation: Concurrent transactions do not interfere; guaranteed via 2-Phase Locking (2PL).
- Durability: Committed updates survive system crashes; guaranteed via Write-Ahead Logging (WAL) and Redo logging."""
    },
    {
        "chunk_id": "study_os_scheduling_deadlock",
        "category": "study_guides",
        "course_code": "CS302",
        "course_name": "Operating Systems",
        "branch": "CSE",
        "semester": 5,
        "source_document": "OS_Quick_Revision_Notes.pdf",
        "page_number": 1,
        "section_heading": "OS CPU Scheduling & Deadlock Formulas",
        "text": """OPERATING SYSTEMS HIGH-YIELD CHEAT SHEET
Key Performance Metrics:
- Turnaround Time = Completion Time - Arrival Time
- Waiting Time = Turnaround Time - Burst Time
- Response Time = Time of first CPU allocation - Arrival Time
Deadlock: 4 Coffman Conditions (Must all hold simultaneously for deadlock):
1. Mutual Exclusion: Resources cannot be shared.
2. Hold and Wait: Process holds >= 1 resource while requesting others.
3. No Preemption: Resources cannot be forcibly seized.
4. Circular Wait: P0 waits for P1, P1 waits for P2, ..., Pn waits for P0.
Deadlock Avoidance - Banker's Algorithm Formulas:
- Need Matrix = Max Matrix - Allocation Matrix
- System is in a SAFE state if there exists at least one execution sequence where Need <= Available for every process."""
    }
]

# -------------------------------------------------------------
# RESOURCE 5: ACADEMIC CALENDAR & MILESTONES
# -------------------------------------------------------------
CALENDAR_RECORDS = [
    {
        "chunk_id": "calendar_even_sem_2025",
        "category": "academic_calendar",
        "course_code": "",
        "course_name": "Academic Calendar",
        "branch": "All",
        "semester": None,
        "source_document": "Academic_Calendar_2024_2025.pdf",
        "page_number": 1,
        "section_heading": "Even Semester Key Dates (Jan - Jun 2025)",
        "text": """OFFICIAL UNIVERSITY ACADEMIC CALENDAR (EVEN SEMESTER 2024-2025)
Semester Schedule:
- Commencement of Classes: January 6, 2025
- Last date for Course Registration / Add-Drop: January 18, 2025
- Mid-Term Examination 1 (CIA-1): February 24 – March 1, 2025
- Mid-Term Marks Display & Feedback Review: March 10, 2025
- Annual University Cultural & Tech Fest (InnovateX): March 21 – March 23, 2025
- Mid-Term Examination 2 (CIA-2): April 21 – April 26, 2025
- Last Instructional Working Day: May 3, 2025
- Final Attendance Shortage & Detention Notification: May 5, 2025
- Laboratory Practical End-Semester Examinations: May 7 – May 13, 2025
- Theory End-Semester Examinations (ESE): May 16 – June 4, 2025
- Summer Vacation & Internship Period: June 5 – July 20, 2025
- Declaration of ESE Results: June 28, 2025"""
    }
]

# -------------------------------------------------------------
# RESOURCE 6: PROFESSIONAL ELECTIVES SYLLABI
# -------------------------------------------------------------
ELECTIVE_RECORDS = [
    {
        "chunk_id": "cs411_meta",
        "category": "curriculum",
        "course_code": "CS411",
        "course_name": "Cryptography & Network Security",
        "branch": "CSE",
        "semester": 7,
        "credits": 3,
        "ltp": "3-0-0",
        "prerequisites": "Computer Networks (CS303), Discrete Mathematics",
        "source_document": "CSE_Electives_Handbook_2025.pdf",
        "page_number": 1,
        "section_heading": "Course Overview & Cryptographic Primitives",
        "text": """Course: CRYPTOGRAPHY & NETWORK SECURITY (CS411)
Credits: 3.0 (L: 3, T: 0, P: 0) | Semester: 7 | Professional Elective | Branch: CSE
Prerequisites: CS303 Computer Networks, Discrete Mathematics.
Course Objectives:
- Study classical ciphers, Shannon's secrecy theory, and modern symmetric cryptography: DES, AES (Rijndael cipher with 128/192/256-bit keys).
- Understand public-key cryptography: RSA algorithm, Diffie-Hellman Key Exchange, Elliptic Curve Cryptography (ECC).
- Explore cryptographic hash functions: SHA-256, SHA-3, Message Authentication Codes (HMAC), and Digital Signatures (DSA, ECDSA).
- Implement network security protocols: IPsec (AH, ESP), SSL/TLS handshake protocol, HTTPS, and Kerberos authentication."""
    },
    {
        "chunk_id": "cs412_meta",
        "category": "curriculum",
        "course_code": "CS412",
        "course_name": "Big Data Analytics",
        "branch": "CSE",
        "semester": 8,
        "credits": 3,
        "ltp": "3-0-0",
        "prerequisites": "Database Management Systems (CS301)",
        "source_document": "CSE_Electives_Handbook_2025.pdf",
        "page_number": 3,
        "section_heading": "Course Overview & Distributed Data Processing",
        "text": """Course: BIG DATA ANALYTICS (CS412)
Credits: 3.0 (L: 3, T: 0, P: 0) | Semester: 8 | Professional Elective | Branch: CSE
Prerequisites: CS301 Database Management Systems, Python / Java.
Course Objectives:
- Master Big Data 5Vs: Volume, Velocity, Variety, Veracity, Value.
- Understand Hadoop ecosystem: Hadoop Distributed File System (HDFS) architecture, NameNode, DataNode, Secondary NameNode, and MapReduce programming paradigm.
- Develop distributed processing pipelines using Apache Spark: Resilient Distributed Datasets (RDDs), Spark DataFrames, Spark SQL, and Spark Streaming.
- Explore NoSQL distributed databases: HBase (column-family), Cassandra, MongoDB (document store), and Neo4j (graph store)."""
    },
    {
        "chunk_id": "cs413_meta",
        "category": "curriculum",
        "course_code": "CS413",
        "course_name": "Mobile Application Development",
        "branch": "CSE",
        "semester": 7,
        "credits": 3,
        "ltp": "3-0-0",
        "prerequisites": "Object-Oriented Programming (Java / Kotlin), Web Technologies (CS305)",
        "source_document": "CSE_Electives_Handbook_2025.pdf",
        "page_number": 5,
        "section_heading": "Course Overview & Android Architecture",
        "text": """Course: MOBILE APPLICATION DEVELOPMENT (CS413)
Credits: 3.0 (L: 3, T: 0, P: 0) | Semester: 7 | Professional Elective | Branch: CSE
Prerequisites: Object-Oriented Programming (Java / Kotlin), CS305 Web Technologies.
Course Objectives:
- Study Android operating system stack: Linux Kernel, Native Libraries, Android Runtime (ART), Application Framework.
- Design mobile UI using Jetpack Compose, XML layouts, Fragments, RecyclerView, and Material Design guidelines.
- Handle application lifecycle, Intents (Explicit vs Implicit), Broadcast Receivers, Background Services, and WorkManager.
- Implement persistent local storage using Room SQLite database and DataStore; consume REST APIs with Retrofit and Coroutines."""
    },
    {
        "chunk_id": "cs414_meta",
        "category": "curriculum",
        "course_code": "CS414",
        "course_name": "DevOps & CI/CD Pipelines",
        "branch": "CSE",
        "semester": 8,
        "credits": 3,
        "ltp": "3-0-0",
        "prerequisites": "Operating Systems (CS302), Cloud Computing (CS403)",
        "source_document": "CSE_Electives_Handbook_2025.pdf",
        "page_number": 7,
        "section_heading": "Course Overview & Infrastructure Automation",
        "text": """Course: DEVOPS & CI/CD PIPELINES (CS414)
Credits: 3.0 (L: 3, T: 0, P: 0) | Semester: 8 | Professional Elective | Branch: CSE
Prerequisites: CS302 Operating Systems, CS403 Cloud Computing.
Course Objectives:
- Master Version Control best practices with Git: Trunk-based development, GitFlow, rebase, cherry-pick, conflict resolution.
- Build continuous integration and deployment pipelines using GitHub Actions, Jenkins, and GitLab CI.
- Package microservices into OCI compliant containers using Docker multi-stage builds.
- Automate cloud infrastructure using Infrastructure-as-Code (Terraform / Ansible) and manage container orchestration with Kubernetes (Pods, Deployments, Services, Ingress)."""
    }
]

# -------------------------------------------------------------
# RESOURCE 7: ADVANCED EXAMINATION & EVALUATION REGULATIONS
# -------------------------------------------------------------
ADVANCED_REGULATION_RECORDS = [
    {
        "chunk_id": "reg_revaluation_script",
        "category": "regulations",
        "course_code": "",
        "course_name": "Academic Regulations",
        "branch": "All Engineering",
        "semester": None,
        "source_document": "Academic_Regulations_2025.pdf",
        "page_number": 6,
        "section_heading": "Clause 8.1: Revaluation & Answer Script Inspection",
        "text": """OFFICIAL ACADEMIC REGULATIONS: REVALUATION PROCEDURE (Clause 8.1)
1. Answer Script Inspection:
   - A student may apply for a digital certified photocopy of their evaluated End-Semester answer script within 7 calendar days of results announcement on payment of Rs. 500 per script.
2. Revaluation Application:
   - If dissatisfied after script inspection, a formal revaluation petition may be submitted within 10 days of photocopy receipt on payment of Rs. 1,000 per subject.
   - The script is re-examined independently by an external senior examiner.
   - If the variance in marks is 15% or higher, the average of the two closest marks is awarded. If marks increase by 10% or more, 50% of the revaluation fee is refunded to the student."""
    },
    {
        "chunk_id": "reg_supplementary_arrear",
        "category": "regulations",
        "course_code": "",
        "course_name": "Academic Regulations",
        "branch": "All Engineering",
        "semester": None,
        "source_document": "Academic_Regulations_2025.pdf",
        "page_number": 7,
        "section_heading": "Clause 8.2: Supplementary & Makeup Examinations",
        "text": """OFFICIAL ACADEMIC REGULATIONS: SUPPLEMENTARY EXAMS (Clause 8.2)
1. Supplementary / Arrear examinations are held twice annually:
   - Summer Supplementary Cycle: Conducted in July for odd and even semester courses.
   - Winter Supplementary Cycle: Conducted in January alongside regular odd semester examinations.
2. Eligibility:
   - Students who obtained an 'F' grade or 'Ab' (Absent on approved medical grounds) in regular exams are eligible to register.
   - Maximum 4 backlog subjects may be registered per supplementary session.
   - The original Continuous Internal Assessment (CIA) marks are carried forward.
   - The highest grade attainable in a supplementary exam is 'A' (Grade Point 8.0)."""
    },
    {
        "chunk_id": "reg_malpractice_penalties",
        "category": "regulations",
        "course_code": "",
        "course_name": "Academic Regulations",
        "branch": "All Engineering",
        "semester": None,
        "source_document": "Academic_Regulations_2025.pdf",
        "page_number": 8,
        "section_heading": "Clause 9.1: Examination Malpractice & Disciplinary Actions",
        "text": """OFFICIAL ACADEMIC REGULATIONS: MALPRACTICE CLAUSES (Clause 9.1)
Categories of Examination Malpractice and Standard University Penalties:
- Category 1: Possession of unauthorized written notes, chits, formulas scribbled on hall tickets, calculators, or body parts.
  Penalty: Cancellation of performance in that specific subject, award of 'F' grade, and forfeiture of exam fee.
- Category 2: Possession or use of electronic gadgets (smartphones, smartwatches, Bluetooth earbuds, programmable calculators) inside examination hall.
  Penalty: Immediate confiscation of device, cancellation of performance in all registered subjects of the current semester, and mandatory disciplinary reprimand.
- Category 3: Impersonation / Proxy examination.
  Penalty: Expulsion of both the candidate and impersonator from the university, forfeiture of degree credentials, and registration of formal Police FIR."""
    }
]

# -------------------------------------------------------------
# RESOURCE 8: EXTENDED CAMPUS FAQS & STUDENT AMENITIES
# -------------------------------------------------------------
CAMPUS_FAQ_RECORDS = [
    {
        "chunk_id": "campus_wifi_it_services",
        "category": "campus_services",
        "course_code": "",
        "course_name": "Campus Student Services",
        "branch": "All",
        "semester": None,
        "source_document": "Campus_Life_Handbook_2025.pdf",
        "page_number": 6,
        "section_heading": "IT Helpdesk, Wi-Fi Setup & Student Portal Credentials",
        "text": """CAMPUS IT & DIGITAL SERVICES DIRECTORY
Wi-Fi Access:
- Network SSID: 'CampusNet-Secure' (802.1X EAP Enterprise authentication).
- Username: University Roll Number (e.g., 21CS1045) | Password: Default is DOB (DDMMYYYY) with prompt to change on first login.
- Hostels, central library, academic blocks, and cafeterias feature high-speed gigabit Wi-Fi 6 connectivity.
IT Helpdesk & Device Registration:
- Location: Computer Center, Ground Floor, Academic Block B.
- MAC Address registration for laptops and tablets: Submit via portal at http://helpdesk.campus.edu or email ithelp@campus.edu.
- Free Student Software: Microsoft Office 365, MATLAB Campus-Wide Suite, Autodesk Student License, and GitHub Student Developer Pack."""
    },
    {
        "chunk_id": "campus_bus_transport",
        "category": "campus_services",
        "course_code": "",
        "course_name": "Campus Student Services",
        "branch": "All",
        "semester": None,
        "source_document": "Campus_Life_Handbook_2025.pdf",
        "page_number": 7,
        "section_heading": "Campus Transportation & University Bus Routes",
        "text": """UNIVERSITY BUS TRANSPORTATION & COMMUTE GUIDELINES
Bus Network & Operations:
- The university operates a fleet of 28 GPS-tracked air-conditioned buses across 14 major city routes.
- Morning Arrival: All buses arrive at campus between 8:20 AM and 8:35 AM.
- Evening Departure: Buses depart from Central Bus Bay at 4:45 PM (regular) and 6:30 PM (special evening bus for sports / lab researchers).
Bus Pass Registration:
- Annual transport fee is payable at the commencement of each academic year through the ERP portal.
- Physical RFID Bus Smart Card must be scanned upon boarding and deboarding."""
    },
    {
        "chunk_id": "campus_sports_gym",
        "category": "campus_services",
        "course_code": "",
        "course_name": "Campus Student Services",
        "branch": "All",
        "semester": None,
        "source_document": "Campus_Life_Handbook_2025.pdf",
        "page_number": 8,
        "section_heading": "Sports Complex, Gymnasium & Recreational Facilities",
        "text": """SPORTS COMPLEX & FITNESS AMENITIES
Timings & Facilities:
- Gymnasium (Men & Women separate sections): Open 6:00 AM to 8:30 AM (morning) and 5:00 PM to 8:30 PM (evening).
- Olympic-size athletic running track, standard FIFA turf football ground, floodlit cricket nets.
- Indoor Sports Arena: 4 wooden synthetic badminton courts, table tennis hall, basketball court, and squash courts.
Equipment Rental & Locker Allotment:
- Sports equipment is issued against college ID cards at the Physical Education Directorate desk."""
    }
]

# -------------------------------------------------------------
# RESOURCE 9: ADDITIONAL TECHNICAL EXAM PREP CHEAT SHEETS
# -------------------------------------------------------------
ADDITIONAL_STUDY_GUIDES = [
    {
        "chunk_id": "study_cn_subnetting_routing",
        "category": "study_guides",
        "course_code": "CS303",
        "course_name": "Computer Networks",
        "branch": "CSE",
        "semester": 5,
        "source_document": "CN_Quick_Revision_Notes.pdf",
        "page_number": 1,
        "section_heading": "CN Subnetting & Routing Formulas Cheat Sheet",
        "text": """COMPUTER NETWORKS HIGH-YIELD REVISION CHEAT SHEET
Subnetting Formulas:
- Number of Subnets created = 2^(subnet bits borrowed)
- Total IP Addresses per Subnet = 2^(host bits)
- Usable Host Addresses = 2^(host bits) - 2 (subtract 1 for Network ID, 1 for Directed Broadcast Address).
- Example: /26 mask (255.255.255.192) has 6 host bits -> 2^6 - 2 = 62 usable hosts per subnet.
OSI Layers & Protocols Quick Reference:
- Layer 7 Application: HTTP/HTTPS, DNS, FTP, SMTP, SSH
- Layer 4 Transport: TCP (reliable, connection-oriented, flow & congestion control), UDP (unreliable, connectionless, low latency)
- Layer 3 Network: IPv4, IPv6, ICMP, OSPF, BGP
- Layer 2 Data Link: Ethernet (802.3), Wi-Fi (802.11), ARP, switches, MAC addressing
- Layer 1 Physical: Bits, cables, hubs, repeaters."""
    },
    {
        "chunk_id": "study_compiler_parsing_cheatsheet",
        "category": "study_guides",
        "course_code": "CS304",
        "course_name": "Compiler Design",
        "branch": "CSE",
        "semester": 6,
        "source_document": "Compiler_Quick_Revision_Notes.pdf",
        "page_number": 1,
        "section_heading": "Compiler Design First/Follow & LR Parsing Cheat Sheet",
        "text": """COMPILER DESIGN HIGH-YIELD REVISION CHEAT SHEET
FIRST and FOLLOW Rules:
- FIRST(X):
  1. If X is terminal, FIRST(X) = {X}.
  2. If X -> epsilon, epsilon in FIRST(X).
  3. If X -> Y1 Y2 ... Yk, add FIRST(Y1) - {epsilon}. If Y1 can derive epsilon, add FIRST(Y2) - {epsilon}, and so on.
- FOLLOW(A):
  1. If A is start symbol, add '$' to FOLLOW(A).
  2. If B -> alpha A beta, add FIRST(beta) - {epsilon} to FOLLOW(A).
  3. If B -> alpha A or B -> alpha A beta where beta -> epsilon, add FOLLOW(B) to FOLLOW(A).
Parser Class Hierarchy:
- LL(1) < SLR(1) < LALR(1) < CLR(1)
- SLR(1): Uses LR(0) items + FOLLOW sets to resolve reduce actions.
- CLR(1): Uses LR(1) items [A -> alpha . beta, a] with lookaheads. Maximum parsing power among deterministic bottom-up parsers, but largest state count.
- LALR(1): Merges CLR(1) states with identical LR(0) cores. Reduces state size to equal SLR(1) without conflict explosion."""
    }
]

ALL_RESOURCES = (
    CURRICULUM_RECORDS +
    ELECTIVE_RECORDS +
    REGULATION_RECORDS +
    ADVANCED_REGULATION_RECORDS +
    CAMPUS_SERVICES_RECORDS +
    CAMPUS_FAQ_RECORDS +
    STUDY_GUIDE_RECORDS +
    ADDITIONAL_STUDY_GUIDES +
    CALENDAR_RECORDS
)

def build_and_index_all_resources() -> Dict[str, Any]:
    """Generates embeddings for all resources and indexes them into Cloudflare Vectorize."""
    logger.info(f"Starting ingestion of {len(ALL_RESOURCES)} chunks across 5 data resources...")

    texts = [r["text"] for r in ALL_RESOURCES]
    embeddings = embedding_service.get_embeddings(texts)

    # Insert into Cloudflare Vectorize
    upserted_count = cloudflare_vector_store.insert_chunks(ALL_RESOURCES, embeddings)

    # Also save comprehensive indexed chunks file for inspection and fast local load
    indexed_data = []
    for r, vec in zip(ALL_RESOURCES, embeddings):
        indexed_data.append({
            **r,
            "embedding": vec
        })

    indexed_file = DATA_DIR / "indexed_chunks.json"
    with open(indexed_file, "w", encoding="utf-8") as f:
        json.dump(indexed_data, f, indent=2)

    logger.info(f"Successfully indexed {upserted_count} chunks into Cloudflare Vectorize")

    summary = {
        "total_chunks": len(ALL_RESOURCES),
        "upserted_count": upserted_count,
        "resources": {
            "curriculum": len(CURRICULUM_RECORDS),
            "regulations": len(REGULATION_RECORDS),
            "campus_services": len(CAMPUS_SERVICES_RECORDS),
            "study_guides": len(STUDY_GUIDE_RECORDS),
            "academic_calendar": len(CALENDAR_RECORDS)
        },
        "vector_store": cloudflare_vector_store.get_index_info()
    }

    # Save resource summary metadata
    with open(DATA_DIR / "resource_catalog.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary

if __name__ == "__main__":
    res = build_and_index_all_resources()
    print("Multi-resource indexing complete:")
    print(json.dumps(res, indent=2))
