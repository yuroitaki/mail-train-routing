## Scope

A Python implementation to solve a variant of capacitated vehicle routing problem.

## Implementation
- Handled mutliple concurrent deliveries of packages using multiple trains
- Achieved more optimal schedule by intermdiate deposit - allowing train to deliver package to an intermediate nearer station to the destination
- Achieved concurrency by always assigning packages to train that is nearest and has done the least deliveries
- Saved computation by storing shortest distance calculated

## Assumption
- Every package can be delivered to its destination
- There is a path from the initial station of the package to its destination
- The weight of a package is not bigger than the biggest train capacity
- There is a path from at least 1 initial station of a train to the initial station of the package 