PATH: posts.UID as UID1 -- PTYPE as PT1 -- QID
              <=> posts.PID -- PTYPE as PT2 -- UID as UID2
FILTER: PT1 == A && PT2 == Q
        COUNT(UID1, UID2) as CNT, CNT >= N
SRC_ATTR: UNAME
DUMMY: dummy
DST_ATTR: UNAME
EDGE_ATTR: CNT
FLAGS: DIRECTED
