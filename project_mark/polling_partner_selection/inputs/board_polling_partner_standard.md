# Polling partner standard

Scenario document. Written by the task author to state the standard the editorial board applies in this task. It
is not a FiveThirtyEight publication. The polling record it is applied to is real and unaltered.

1. Purpose. For each midterm cycle the board selects one polling partner: the eligible pollster with the lowest
   certified error among those that pass the test cycle.

2. The record. The current vintage of the raw polls file in the workspace. The polls used are general election
   polls, which are the rows whose simple type ends in G, the generic ballot included, from the cycles 2016
   through 2022 inclusive.

3. Unit and error. The unit is the poll, identified by its poll id. A question's error is the absolute difference
   in points between the poll margin and the actual margin. A poll's error is the mean of its questions' errors.
   A pollster's certified error is the mean of its polls' errors, stated to two decimal places.

4. Eligibility. A pollster is eligible when it is active, none of its polls in the record is flagged partisan, it
   has at least 40 polls in the record, and it has at least 10 polls in the test cycle.

5. The test cycle. The test cycle is the most recent midterm cycle in the record. A pollster passes when its mean
   poll error in the test cycle does not exceed the median poll error of every poll in the test cycle in the
   record, all pollsters included.

6. Selection. Among eligible pollsters that pass, the one with the lowest certified error; where two are equal to
   two decimals, the one with more polls in the record.

7. Identity. A pollster is identified by its pollster rating id, which is stable across vintages of the record;
   pollster names are not.

8. Previous selection. The partner for the 2022 cycle was selected on the record's 2021 vintage, with the cycles
   2014 through 2020 as the record and 2020 as the test cycle, under these rules (that vintage carries no activity
   flag, so the activity test did not apply): Emerson College, 4.62 points.

9. Record figures. Where a pollster's bias or winner calls are reported, they are taken over its questions in the
   record, because one poll can cover more than one race: a question's bias is its poll margin less the actual
   margin, positive when the Democratic margin is overstated, and the pollster's bias is the mean over its
   questions; a question calls the winner when its poll margin and the actual margin have the same sign, a
   question with a zero poll margin is not a call, and the call rate is over questions that make a call.
