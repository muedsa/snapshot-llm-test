# B06 作品集策展

《信息，重建》用十种不同的视觉逻辑处理十个日常信息卡点：先看清变化、路线、完整成本、单位价、依赖、条款、假设、去向、影响或测试点，再采取有限的下一步。

## B06-case-01 · Why Did This Month's Bill Change?

- 受众：A householder trying to understand an unexpected electricity bill
- 场景：A4-style portrait explainer next to a monthly statement
- 目标：Identify which charges changed, by how much, and what action or question each change suggests.
- 视觉：A waterfall from $104 to $142 with only changed components rising, plus a compact 'ask/check/do' rail that converts each line into an action.
- 内容：{'problem_evidence': 'A total and line items hide the bridge between last month and this month; design hypothesis only, no user study.', 'type': 'fictional demonstration', 'demo_values': {'previous_total': 104, 'current_total': 142, 'difference': 38, 'previous': {'service': 18, 'energy': 65, 'delivery': 22, 'taxes': 6, 'credit': -7}, 'current': {'service': 18, 'energy': 99, 'delivery': 22, 'taxes': 9, 'credit': -6}}, 'arithmetic': 'Previous components sum to 104; current components sum to 142; change +34 energy, +3 taxes, +1 credit, total +38.', 'limitations': 'Amounts are invented USD demonstration values. No tariff, tax rule, or utility provider is represented.'}
- [查看作品](B06-case-01/final.png) · [完整DSL](B06-case-01/final.snapshot) · [用例说明](B06-case-01/case.md)

## B06-case-02 · Can I Still Get There?

- 受众：A commuter facing a partial train-line disruption
- 场景：Landscape station display and mobile companion view
- 目标：Determine whether the destination is still reachable, which stations are affected, and where to change or wait.
- 视觉：A service-state graph where the closed segment becomes a broken rail bridged by a bus ribbon; the user's origin/destination remain anchored while unaffected service recedes.
- 内容：{'problem_evidence': 'A line diagram shows geography but not service state; a disruption list shows state but not journey consequence. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'line': 'Blue Line', 'closed_segment': 'Harbor–Market', 'origin': 'Harbor', 'destination': 'Museum', 'replacement_bus': 'Harbor–Market', 'remaining_train': 'Market–Museum', 'extra_minutes': 12}, 'limitations': 'All stations, service states, times, and the replacement bus are fictional. This is not live transit information.'}
- [查看作品](B06-case-02/final.png) · [完整DSL](B06-case-02/final.snapshot) · [用例说明](B06-case-02/case.md)

## B06-case-03 · Which Home Is Actually Affordable?

- 受众：A renter comparing listings with different fees and included utilities
- 场景：Portrait comparison sheet used during an apartment search
- 目标：Compare complete recurring monthly cost and one-time entry cost instead of headline rent alone.
- 视觉：Three vertical cost stacks rise from a shared baseline, with recurring and one-time costs deliberately separated and a value-for-space strip that does not hide total cost.
- 内容：{'problem_evidence': 'Listings separate rent, utilities, parking, laundry, and deposits, making the recurring total hard to compare. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'A': {'rent': 1450, 'utilities_estimate': 180, 'parking': 35, 'laundry': 0, 'monthly_total': 1665, 'entry_fees': 500}, 'B': {'rent': 1320, 'utilities_estimate': 230, 'parking': 0, 'laundry': 60, 'monthly_total': 1610, 'entry_fees': 350}, 'C': {'rent': 1550, 'utilities_estimate': 140, 'parking': 120, 'laundry': 0, 'monthly_total': 1810, 'entry_fees': 600}}, 'arithmetic': 'A: 1450+180+35=1665. B: 1320+230+60=1610. C: 1550+140+120=1810.', 'limitations': 'All amounts are fictional USD demonstration values. Utility figures are estimates; entry fees are shown separately and excluded from monthly totals.'}
- [查看作品](B06-case-03/final.png) · [完整DSL](B06-case-03/final.snapshot) · [用例说明](B06-case-03/case.md)

## B06-case-04 · The Better Price per Kilogram

- 受众：A shopper comparing two pack sizes under time pressure
- 场景：Shelf-edge portrait card and phone shopping companion
- 目标：Compare unit price while seeing upfront cost, likely usable quantity, and expiry/waste risk.
- 视觉：Two oversized shelf tags joined by a common per-kilogram ruler, with a lower waste-risk band that prevents unit price from becoming the only answer.
- 内容：{'problem_evidence': 'Pack sizes and promotion labels differ, so shoppers must normalize price and quantity mentally while also considering waste. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'A': {'mass_g': 850, 'price': 5.1, 'price_per_kg': 6.0, 'expiry_days': 10}, 'B': {'mass_g': 500, 'price': 3.3, 'price_per_kg': 6.6, 'expiry_days': 5}}, 'arithmetic': 'A: 5.10/0.850=$6.00/kg. B: 3.30/0.500=$6.60/kg. A is $0.60/kg cheaper but costs $1.80 more upfront.', 'limitations': 'Product, prices, masses, and expiry days are fictional demonstration values; no nutrition or health claim.'}
- [查看作品](B06-case-04/final.png) · [完整DSL](B06-case-04/final.snapshot) · [用例说明](B06-case-04/case.md)

## B06-case-05 · What Should I Do First?

- 受众：A university student juggling interdependent assignments
- 场景：Portrait study-planning poster and phone companion
- 目标：See which assignment unlocks others, estimate effort, and choose a realistic next action before the nearest deadline.
- 视觉：A dependency river from outline to final, with deadline gates and effort stones; the nearest actionable step is highlighted without implying that all tasks are equal-sized.
- 内容：{'problem_evidence': 'A chronological deadline list hides dependencies and effort, so equal urgency can conceal very different next steps. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'outline': {'due': '2026-12-02', 'weight': 20, 'effort_hours': 3, 'unlocks': ['draft']}, 'draft': {'due': '2026-12-05', 'weight': 30, 'effort_hours': 6, 'unlocks': ['peer_review']}, 'peer_review': {'due': '2026-12-08', 'weight': 10, 'effort_hours': 2, 'unlocks': ['final']}, 'final': {'due': '2026-12-12', 'weight': 40, 'effort_hours': 5}}, 'arithmetic': 'Weights sum to 100%; planned effort sums to 16 hours.', 'limitations': 'Course, dates, weights, and effort estimates are fictional. Effort is a planning estimate, not measured productivity.'}
- [查看作品](B06-case-05/final.png) · [完整DSL](B06-case-05/final.snapshot) · [用例说明](B06-case-05/case.md)

## B06-case-06 · Is This Kind of Damage Covered?

- 受众：A policyholder trying to understand a home-insurance scenario before calling support
- 场景：Portrait decision guide beside a fictional policy summary
- 目标：Follow a scenario from event description to relevant policy section, exclusions, documentation, and the next question to ask.
- 视觉：A branching scenario tree that narrows from event to policy section to exclusion check, ending in a document checklist rather than a false yes/no verdict.
- 内容：{'problem_evidence': "Policy wording is organized by legal sections rather than the user's event; exclusions and conditions are hard to connect to a real scenario. Design hypothesis only.", 'type': 'fictional demonstration', 'demo_values': {'event': 'Burst pipe damages kitchen floor', 'relevant_section': 'Section 4: Sudden accidental water escape', 'exclusion_to_check': 'Gradual leakage exclusion', 'documents': ['photos', 'plumber report', 'receipts'], 'outcome': 'Needs adjuster review; no coverage decision is claimed.'}, 'limitations': 'Policy language and scenario are fictional and simplified. The artwork must state that it is not legal advice or a real coverage determination.'}
- [查看作品](B06-case-06/final.png) · [完整DSL](B06-case-06/final.snapshot) · [用例说明](B06-case-06/case.md)

## B06-case-07 · Repair It or Replace It?

- 受众：A householder deciding what to do after an appliance failure
- 场景：Portrait decision card beside a repair quote
- 目标：Compare immediate cost, remaining-life assumptions, warranty status, and non-price factors before choosing a next step.
- 视觉：A two-sided decision dial with repair and replacement cost-per-year arcs, plus a warranty gate and a small non-price factors tray.
- 内容：{'problem_evidence': 'Repair quotes and replacement prices are incomparable without remaining-life and warranty context. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'appliance': 'Refrigerator', 'repair_cost': 220, 'replacement_cost': 780, 'repair_remaining_years': 4, 'replacement_assumed_years': 8, 'repair_cost_per_year': 55, 'replacement_cost_per_year': 97.5, 'warranty': 'expired'}, 'arithmetic': '220/4=$55 per assumed year; 780/8=$97.50 per assumed year.', 'limitations': 'All costs and life assumptions are fictional and exclude energy, disposal, installation, and future failures. The result is conditional, not a universal recommendation.'}
- [查看作品](B06-case-07/final.png) · [完整DSL](B06-case-07/final.snapshot) · [用例说明](B06-case-07/case.md)

## B06-case-08 · Where Does This Actually Go?

- 受众：A resident unsure how to sort six ambiguous household items
- 场景：Portrait kitchen-side recycling guide
- 目标：Sort each item by material and condition, identify contamination risks, and find the correct next action for non-curbside items.
- 视觉：Six illustrated items travel down a sorting conveyor into labelled routes; condition tags and special-drop-off branches prevent a simple colour-bin chart.
- 内容：{'problem_evidence': 'Material symbols and accepted-item lists do not always explain condition, preparation, or special drop-off requirements. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'city': 'Harbor City (fictional)', 'items': [{'item': 'Clean paper', 'route': 'paper recycling', 'prep': 'clean and dry'}, {'item': 'Greasy pizza box', 'route': 'organics if accepted', 'prep': 'remove clean lid'}, {'item': 'Rigid plastic bottle', 'route': 'plastics recycling', 'prep': 'empty, cap on'}, {'item': 'Soft plastic bag', 'route': 'store drop-off', 'prep': 'not curbside'}, {'item': 'Battery', 'route': 'battery drop-off', 'prep': 'tape terminals'}, {'item': 'Glass jar', 'route': 'glass recycling', 'prep': 'rinse, no ceramics'}]}, 'limitations': 'Harbor City and every rule are fictional. The artwork must not be used as real local recycling guidance.'}
- [查看作品](B06-case-08/final.png) · [完整DSL](B06-case-08/final.snapshot) · [用例说明](B06-case-08/case.md)

## B06-case-09 · What Decision Affects My Block?

- 受众：A resident scanning a long public-meeting agenda
- 场景：Landscape civic agenda map before a neighborhood meeting
- 目标：Find agenda items by personal impact, understand what decision is being made, and know when and how to comment.
- 视觉：A neighborhood impact map surrounded by four agenda cards, each connected to the place and people affected; a comment-deadline rail makes participation concrete.
- 内容：{'problem_evidence': 'Agendas are ordered by procedure and department, not by who is affected or what action residents can take. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'meeting': 'District 4 Community Meeting (fictional)', 'items': [{'item': 'School crossing timing', 'impact': 'families on Oak Street', 'decision': 'approve trial timing', 'comment_by': '2026-12-01'}, {'item': 'Park hours', 'impact': 'evening park users', 'decision': 'extend closing to 22:00', 'comment_by': '2026-12-03'}, {'item': 'Bus lane pilot', 'impact': 'drivers and bus riders on 3rd Avenue', 'decision': 'approve six-month pilot', 'comment_by': '2026-12-04'}, {'item': 'Tree removal request', 'impact': 'residents near Cedar Court', 'decision': 'approve or deny removal', 'comment_by': '2026-12-05'}]}, 'limitations': 'Meeting, district, locations, decisions, and deadlines are fictional. The map is an agenda reordering demonstration, not an official notice.'}
- [查看作品](B06-case-09/final.png) · [完整DSL](B06-case-09/final.snapshot) · [用例说明](B06-case-09/case.md)

## B06-case-10 · Fix the Room, Not the Whole House

- 受众：A householder troubleshooting weak Wi-Fi in one room
- 场景：Landscape home floor-plan diagnostic
- 目标：Locate the likely weak-signal area, test one change at a time, and choose a proportionate next action.
- 视觉：A clean floor plan with signal contours, one highlighted test point, and a three-step action rail; the weakest room is obvious without turning the whole house into a heat map.
- 内容：{'problem_evidence': 'Router status pages report house-level connection health while users experience room-level dead zones. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'router': 'living room', 'signal_demo': {'living_room': -42, 'bedroom': -58, 'kitchen': -72}, 'actions': ['move router higher and away from the microwave', 'test kitchen again in the same spot', 'add a mesh point only if the test still fails']}, 'limitations': 'Floor plan, signal values in dBm, device locations, and actions are fictional. The guide must not claim a guaranteed fix or a measured survey.'}
- [查看作品](B06-case-10/final.png) · [完整DSL](B06-case-10/final.snapshot) · [用例说明](B06-case-10/case.md)
