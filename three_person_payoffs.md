# Three-person attendance game: proposed payoffs

**Provenance.** The payoff below is our proposed one-day specification, not an equation copied from the telecommuting paper. Its cost-of-distancing versus expected cost-of-infection structure follows the modeling idea in [Reluga (2010)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000793); the three-person network, exact probability, and numerical costs are choices made for this exercise.

**Purpose.** This is a one-day, three-player game to discuss individual incentives before adding game decisions to the SIS simulation. People 1, 2, and 3 all know one another, so the potential contact network is the complete graph $K_3$. For the first example, the infection states at the start of the day are public: person 1 is infected and persons 2 and 3 are susceptible. This information assumption is part of the proposed game, not a claim about real workplaces.

**Actions and timing.** Each person simultaneously chooses $A$ (attend) or $H$ (stay home). A pair has an on-site contact only if both choose $A$. In this first game, staying home removes all contacts in this three-person network. Transmission and recovery are evaluated from the *start-of-day* infection states; changes take effect at the end of the day, as in the SIS simulation. An initially infected person transmits during the day and recovers with probability $\gamma$ at its end. A susceptible person who becomes infected can recover on a later day and then be infected again.

**Infection risk.** Let $\beta$ be the probability of transmission across one active infected-susceptible edge in one day. For a susceptible person $i$, let $m_i(a,x)$ count the initially infected people who attend alongside $i$; set $m_i=0$ if $i$ stays home. Assuming independent transmission attempts, the probability that $i$ ends the day infected is

$$
q_i(a,x)=1-(1-\beta)^{m_i(a,x)}.
$$

For someone already infected at the start of the day, $q_i(a,x)=1-\gamma$, independent of attendance. This is the probability of *remaining infected at day's end*.

**Payoff.** Let $c_i>0$ be person $i$'s cost of staying home for one day, such as lost work or social activity. Let $L_i>0$ be the cost of ending the day infected. Taking attendance as the zero-cost baseline, the expected one-day payoff is

$$
U_i(a\mid x)=-c_i\,\mathbf{1}\{a_i=H\}-L_i\,q_i(a,x).
$$

These are expected *private* payoffs. Infection costs can differ by person. There is no policy penalty, reward, altruism, household transmission, or outside infection in this first game; each would require an explicit additional term.

**A concrete three-person example.** Set $c_i=0.2$, $L_i=10$, $\beta=0.04$, and $\gamma=0.20$ for everyone. If infected person 1 attends, either susceptible person's payoff from attending is $-10(0.04)=-0.4$, while staying home gives $-0.2$; each prefers home. Person 1's expected infection cost is $10(0.8)=8$ whether attending or staying home, so attending avoids the additional $0.2$ home cost. Thus $(A,H,H)$ is a Nash equilibrium in this specified one-day game. The example exposes an infection externality: person 1's attendance changes others' risk but not person 1's own infection risk. A later policy or repeated-game model could change that incentive, but its payoff terms should be agreed before coding.
