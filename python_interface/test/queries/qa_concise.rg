PATH: p1(posts).OwnerUserId -> ParentId => p2(posts).Id -> OwnerUserId
FILTER: p1.PostTypeId == 2 && p2.PostTypeId == 1
