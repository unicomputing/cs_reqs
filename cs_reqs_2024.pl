c_or_higher(Grade) :- memberchk(Grade, ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']).

% upper_division() :- 

% GPA() :- 


% taken(Id, Credits, Grade, When, Where): taken course Id with Credits, etc.

passed(Id) :- taken(Id, Credits_, Grade, When_, Where_), c_or_higher(Grade).

% c(Id, Subject): course Id in Subject

% passed all courses in subject Subj
passed_all(Subj) :- forall(c(Id, Subj), passed(Id)).



% 1. Required Introductory Courses

c('CSE 114', prog). c('CSE 214', prog). c('CSE 216', prog). 
c('CSE 160', prog2). c('CSE 161', prog2). 
c('CSE 260', prog2). c('CSE 261', prog2).
c('CSE 215', dmath). 
c('CSE 150', dmath2).
c('CSE 220', sys). 

intro_courses(Id) :-
  c(Id, prog); c(Id, prog2); c(Id, dmath); c(Id, dmath2); c(Id, sys).

intro_req :-
  (passed_all(prog); passed_all(prog2)),
  (passed_all(dmath); passed_all(dmath2)),
  passed_all(sys).

% 2.


% test

taken_id('CSE 114'). taken_id('CSE 214'). taken_id('CSE 216').
taken_id('CSE 215'). taken_id('CSE 220'). 
taken_id('CSE 303'). taken_id('CSE 310'). taken_id('CSE 316').
taken_id('CSE 320'). taken_id('CSE 373'). taken_id('CSE 416').
taken_id('MAT 131'). taken_id('MAT 132'). 
taken_id('AMS 210'). taken_id('AMS 301'). taken_id('AMS 310'). 
taken_id('CSE 300'). taken_id('CSE 312').

taken_id('CSE 360'). taken_id('CSE 361'). taken_id('CSE 351').
taken_id('CSE 352'). taken_id('CSE 353'). taken_id('CSE 355').

taken_id('PHY 131'). taken_id('PHY 133'). taken_id('AST 203').

taken(Id, 4, 'A', (2024,2), 'SB') :- taken_id(Id).

test :- intro_req.


% could define forall using findall, avoid negation, but not as efficient
% fa_forall(P, Q) :- findall(Q, P, QList), all_true(QList).
% all_true([]).
% all_true([Q|Qs]) :- call(Q), all_true(Qs).
