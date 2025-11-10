% Facts from the Case
advanced_degree_professional(petitioner).
proposed_endeavor(petitioner, logistics_company).
endeavor_attributes(logistics_company, [substantial_merit, national_importance]).
well_positioned(petitioner, logistics_company).
waiver_beneficial(logistics_company).

% Legal Rules
qualifies_eb2(Petitioner) :-
    advanced_degree_professional(Petitioner).

endeavor_has_substantial_merit_and_national_importance(Endeavor) :-
    endeavor_attributes(Endeavor, Attributes),
    member(substantial_merit, Attributes),
    member(national_importance, Attributes).

satisfies_dhanasar(Petitioner, Endeavor) :-
    endeavor_has_substantial_merit_and_national_importance(Endeavor),
    well_positioned(Petitioner, Endeavor),
    waiver_beneficial(Endeavor).

% Single decision rule with clear logic
decision(Petitioner, Result) :-
    qualifies_eb2(Petitioner),
    proposed_endeavor(Petitioner, Endeavor),
    (   satisfies_dhanasar(Petitioner, Endeavor)
    ->  Result = approved
    ;   Result = dismissed
    ).

% Fallback if EB-2 qualification fails
decision(Petitioner, dismissed) :-
    \+ qualifies_eb2(Petitioner).
