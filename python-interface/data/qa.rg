PATH: posts.OwnerUserId as UID1 -- PostTypeId as PT1 -- ParentId
              <=> posts.Id -- PostTypeId as PT2 -- OwnerUserId as UID2
FILTER: PT1 == 2 && PT2 == 1
