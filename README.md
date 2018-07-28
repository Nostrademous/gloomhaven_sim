# gloomhaven_sim
Gloomhaven Simulator for AI

### Launch Process

1) Launch Game Orchestrator
    * Select Game (i.e., Gloomhaven)
    * Select Party Composition
    * Update Party
        * City Quest (if applicable)
        * Leveling, Items, Perks, etc. (as applicable)
        * Select Ability Cards to Use
        * Update Attack Modifier Decks (due to items, perks, etc.)
    * Select Scenario

2) Launch Scenario Orchestrator
    * Perform Road Event (if applicable)
    * Load Scenario (maps, monster info, treasures, traps, etc.)
    * Load Party into Scenario in Parallel Threads (one per player)
        * First-come First-serve starting position selection
    * Run Scenario (WHILE LOOP)
        * Start Turn
            * Parallel Player Action Selection (Cards from Selected Deck || Long Rest)
            * Join Parallel Player Threads, Draw Monster Ability Cards and Order Actions in Initiative order
        * Execute Turn (sequentially)
            * End Turn for Each Player upon completion (removing effects as appropriate)
                * If Long Rest - untap items appropriately and return discarded ability cards (losing one)
        * End Turn
            * Update Elements Board
            * Allow each Player to Short Rest (optionally)
    * End Scenario
        * Update Gold (based on coin collection)
        * Update XP (if Scenario successful)