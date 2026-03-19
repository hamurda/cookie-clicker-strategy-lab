# Visualization. 

I need three charts. 
1. A CpS-over-time line chart with all three strategies overlaid — this is my hero image for everything. 
2. A purchase timeline showing when each strategy bought what. 
3. Final building inventory comparison — stacked bar chart showing what each strategy ended up with. These tell the whole story visually.

For color scheme, keep it simple — three distinct colors, one per strategy. Label them clearly. No need for anything fancy. The data tells the story.

## The CpS-over-time chart is the most important visual. 
Three lines on the same axes — Greedy ROI, LLM Planner, Buy Cheapest — all starting from the same point at tick 0 (which is really tick 35,000 of the full game).
The interesting things this chart will show: all three lines start at the same CpS (~7,045,000). They stay flat for different amounts of time (greedy saves, LLM buys quickly, cheapest buys constantly). Then they diverge. The greedy line should have a staircase pattern — flat while saving, sharp jumps on purchases. The LLM planner should have a burst of jumps early (the first plan executes fast) then long flat stretches. Buy cheapest should have tiny frequent steps that look almost like a gentle slope.
By tick 5,000, greedy is on top at 8.77M, LLM planner is at 8.31M, and cheapest is at 7.57M. The visual gap tells the story.

## The purchase timeline would be a scatter plot or event plot. 
X-axis is ticks, one row per strategy. 
Each dot is a purchase, colored by type — buildings in one color family, upgrades in a highlight color. This immediately shows: greedy buys steadily throughout, LLM planner clusters purchases in bursts then goes silent, cheapest is a constant stream of dots. The LLM planner's gaps are visible and dramatic.

## Building inventory bar chart
Group by strategy with building types on the x-axis. This shows greedy ended up with 3 Shipments while LLM planner only got 2 and cheapest got zero. It shows cheapest bought 129 cursors while greedy bought 58. The spending priorities are immediately obvious.


# Data to use in visuals

@35k_greedy_roi.json -> This file has the starting Game State. Same state for all 3 Strategies.

## Data for LLM Strategy

@40k_llm_planner_v2.json -> Game State at the end of the simulation

--- Time Series (every 100 ticks) ---
  Tick |          CpS |           Bank |      Total Baked
----------------------------------------------------------
   100 |   7091702.69 |   122903067.20 |      74997319211
   200 |   7238439.76 |    44759064.27 |      75710050676
   300 |   7262815.09 |    80186593.29 |      76434904486
   400 |   7282654.83 |   189748799.96 |      77162034809
   500 |   7282654.83 |   918014282.63 |      77890300292
   600 |   7282654.83 |  1646279765.29 |      78618565774
   700 |   7282654.83 |  2374545247.96 |      79346831257
   800 |   7282654.83 |  3102810730.63 |      80075096740
   900 |   7282654.83 |  3831076213.29 |      80803362222
  1000 |   7490041.49 |   488922139.29 |      81545107838
  1100 |   7490041.49 |  1237926288.63 |      82294111988
  1200 |   7490041.49 |  1986930437.96 |      83043116137
  1300 |   7490041.49 |  2735934587.29 |      83792120286
  1400 |   7490041.49 |  3484938736.63 |      84541124436
  1500 |   7490041.49 |  4233942885.96 |      85290128585
  1600 |   7490041.49 |  4982947035.29 |      86039132734
  1700 |   7764237.49 |   158125748.63 |      86810260804
  1800 |   7771302.11 |   657072751.07 |      87587324283
  1900 |   7771302.11 |  1434202961.73 |      88364454494
  2000 |   7847055.71 |   695128733.20 |      89148251021
  2100 |   7847055.71 |  1479834303.87 |      89932956592
  2200 |   7847055.71 |  2264539874.53 |      90717662163
  2300 |   7847055.71 |  3049245445.20 |      91502367733
  2400 |   7847055.71 |  3833951015.87 |      92287073304
  2500 |   7847055.71 |  4618656586.53 |      93071778875
  2600 |   8054442.37 |   725542313.20 |      93875149245
  2700 |   8054442.37 |  1530986550.53 |      94680593483
  2800 |   8054442.37 |  2336430787.87 |      95486037720
  2900 |   8054442.37 |  3141875025.20 |      96291481957
  3000 |   8054442.37 |  3947319262.53 |      97096926195
  3100 |   8054442.37 |  4752763499.87 |      97902370432
  3200 |   8054442.37 |  5558207737.20 |      98707814669
  3300 |   8314442.37 |   514511974.53 |      99529118907
  3400 |   8314442.37 |  1345956211.87 |     100360563144
  3500 |   8314442.37 |  2177400449.20 |     101192007381
  3600 |   8314442.37 |  3008844686.53 |     102023451619
  3700 |   8314442.37 |  3840288923.87 |     102854895856
  3800 |   8314442.37 |  4671733161.20 |     103686340093
  3700 |   8314442.37 |  3840288923.87 |     102854895856
  3800 |   8314442.37 |  4671733161.20 |     103686340093
  3900 |   8314442.37 |  5503177398.53 |     104517784331
  4000 |   8314442.37 |  6334621635.87 |     105349228568
  4100 |   8314442.37 |  7166065873.20 |     106180672805
  4200 |   8314442.37 |  7997510110.53 |     107012117043
  4300 |   8314442.37 |  8828954347.87 |     107843561280
  4400 |   8314442.37 |  9660398585.20 |     108675005517
  4500 |   8314442.37 | 10491842822.53 |     109506449755
  4600 |   8314442.37 | 11323287059.87 |     110337893992
  4700 |   8314442.37 | 12154731297.20 |     111169338229
  4800 |   8314442.37 | 12986175534.53 |     112000782467
  4900 |   8314442.37 | 13817619771.87 |     112832226704
  5000 |   8314442.37 | 14649064009.20 |     113663670941

--- End-of-Run Summary ---
Final CpS:                8314442.37
Total cookies baked:    113663670941
Total purchases:                  42
Upgrades purchased:                1
Avg ticks between purchases:     79.0
Real time:                  366.2s

Upgrades purchased:
  Factory tier 4

Buildings owned & CpS share:
  Cursor         owned:   64   CpS share:   0.0%
  Grandma        owned:  107   CpS share:   2.6%
  Farm           owned:   67   CpS share:   0.2%
  Mine           owned:   61   CpS share:   0.8%
  Factory        owned:   54   CpS share:   3.7%
  Bank           owned:   43   CpS share:   7.3%
  Temple         owned:   32   CpS share:  29.2%
  Wizard Tower   owned:   20   CpS share:  49.9%
  Shipment       owned:    2   CpS share:   6.3%
  Alchemy Lab    owned:    0   CpS share:   0.0%


  [tick=1] buy_upgrade -> Factory grandma synergy
  [tick=2] buy_building -> Factory
  [tick=3] buy_building -> Factory
  [tick=4] buy_building -> Factory
  [tick=5] buy_building -> Bank
  [tick=6] buy_building -> Mine
  [tick=7] buy_building -> Mine
  [tick=8] buy_building -> Farm
  [tick=38] buy_building -> Grandma
  [tick=39] buy_building -> Factory
  [tick=51] buy_building -> Factory
  [tick=51] buy_building -> Factory
  [tick=66] buy_building -> Factory
  [tick=83] buy_building -> Factory
  [tick=175] buy_upgrade -> Factory tier 4
  [tick=194] buy_building -> Factory
  [tick=217] buy_building -> Factory
  [tick=268] buy_building -> Bank
  [tick=269] buy_building -> Farm
  [tick=274] buy_building -> Mine 
  [tick=275] buy_building -> Farm
  [tick=276] buy_building -> Cursor 
  [tick=277] buy_building -> Cursor
  [tick=278] buy_building -> Cursor
  [tick=281] buy_building -> Mine
  [tick=282] buy_building -> Cursor
  [tick=283] buy_building -> Cursor
  [tick=284] buy_building -> Farm
  [tick=285] buy_building -> Cursor
  [tick=286] buy_building -> Cursor
  [tick=287] buy_building -> Cursor
  [tick=288] buy_building -> Farm
  [tick=289] buy_building -> Mine
  [tick=315] buy_building -> Factory
  [tick=374] buy_building -> Bank
  [tick=935] buy_building -> Wizard Tower
  [tick=1616] buy_building -> Shipment
  [tick=1680] buy_building -> Bank
  [tick=1708] buy_building -> Factory
  [tick=1715] buy_building -> Mine
  [tick=1716] buy_building -> Farm
  [tick=1717] buy_building -> Cursor
  [tick=1912] buy_building -> Temple
  [tick=2510] buy_building -> Wizard Tower
  [tick=3239] buy_building -> Shipment

## Data for Greedy ROI Strategy

@40k_greedy_roi.json -> Game State at the end of the simulation

--- Time Series (every 100 ticks) ---
  Tick |          CpS |           Bank |      Total Baked
----------------------------------------------------------
   100 |   7045123.15 |  1312055681.16 |      74993830452
   200 |   7045123.15 |  2016567995.83 |      75698342767
   300 |   7045123.15 |  2721080310.49 |      76402855081
   400 |   7045123.15 |  3425592625.16 |      77107367396
   500 |   7252216.48 |    47447809.83 |      77813122271
   600 |   7252216.48 |   772669457.83 |      78538343919
   700 |   7252216.48 |  1497891105.83 |      79263565567
   800 |   7252216.48 |  2223112753.83 |      79988787215
   900 |   7252216.48 |  2948334401.83 |      80714008863
  1000 |   7252216.48 |  3673556049.83 |      81439230511
  1100 |   7252216.48 |  4398777697.83 |      82164452159
  1200 |   7512216.48 |    24779345.83 |      82890453807
  1300 |   7512216.48 |   776000993.83 |      83641675455
  1400 |   7587845.28 |     4351885.83 |      84392897103
  1500 |   7619580.91 |    73991215.20 |      85152895295
  1600 |   7619580.91 |   835949305.87 |      85914853386
  1700 |   7619580.91 |  1597907396.53 |      86676811477
  1800 |   7619580.91 |  2359865487.20 |      87438769567
  1900 |   7619580.91 |  3121823577.87 |      88200727658
  2000 |   7619580.91 |  3883781668.53 |      88962685749
  2100 |   7619580.91 |  4645739759.20 |      89724643839
  2200 |   7840597.76 |   418852852.76 |      90506611290
  2300 |   7840597.76 |  1202912628.76 |      91290671066
  2400 |   7916476.16 |   237947387.76 |      92077007194
  2500 |   7916476.16 |  1029595003.76 |      92868654810
  2600 |   7916476.16 |  1821242619.76 |      93660302426
  2700 |   7916476.16 |  2612890235.76 |      94451950042
  2800 |   7916476.16 |  3404537851.76 |      95243597658
  2900 |   7916476.16 |  4196185467.76 |      96035245274
  3000 |   7916476.16 |  4987833083.76 |      96826892890
  3100 |   7916476.16 |  5779480699.76 |      97618540506
  3200 |   8194497.84 |   264284467.44 |      98434103457
  3300 |   8208749.84 |   709950958.44 |      99254778913
  3400 |   8208749.84 |  1530825942.44 |     100075653897
  3500 |   8208749.84 |  2351700926.44 |     100896528881
  3600 |   8208749.84 |  3172575910.44 |     101717403865
  3700 |   8208749.84 |  3993450894.44 |     102538278849
  3800 |   8208749.84 |  4814325878.44 |     103359153833
  3900 |   8416723.17 |   240066775.77 |     104185852071
  4000 |   8416723.17 |  1081739093.11 |     105027524388
  4100 |   8416723.17 |  1923411410.44 |     105869196705
  4200 |   8492726.37 |   757851438.57 |     106717633308
  4300 |   8492726.37 |  1607124075.91 |     107566905945
  4400 |   8492726.37 |  2456396713.24 |     108416178582
  4500 |   8492726.37 |  3305669350.57 |     109265451220
  4600 |   8492726.37 |  4154941987.91 |     110114723857
  4700 |   8492726.37 |  5004214625.24 |     110963996494
  4800 |   8492726.37 |  5853487262.57 |     111813269132
  4900 |   8492726.37 |  6702759899.91 |     112662541769
  5000 |   8771218.13 |   297190196.48 |     113537345126

--- End-of-Run Summary ---
Final CpS:                8771218.13
Total cookies baked:    113537345126
Total purchases:                  27
Upgrades purchased:                0
Avg ticks between purchases:    172.0
Real time:                    0.1s

Buildings owned & CpS share:
  Cursor         owned:   58   CpS share:   0.0%
  Grandma        owned:  110   CpS share:   2.6%
  Farm           owned:   64   CpS share:   0.2%
  Mine           owned:   58   CpS share:   0.8%
  Factory        owned:   47   CpS share:   1.5%
  Bank           owned:   41   CpS share:   6.7%
  Temple         owned:   34   CpS share:  29.5%
  Wizard Tower   owned:   21   CpS share:  49.9%
  Shipment       owned:    3   CpS share:   8.9%
  Alchemy Lab    owned:    0   CpS share:   0.0%


## Data for Buy Cheapest Strategy

@40k_cheapest.json -> Game State at the end of the simulation

--- Time Series (every 100 ticks) ---
  Tick |          CpS |           Bank |      Total Baked
----------------------------------------------------------
   100 |   7061002.24 |    66020041.16 |      74994333936
   200 |   7069730.67 |    80938110.56 |      75700956135
   300 |   7077931.73 |    84425508.52 |      76408420848
   400 |   7083578.35 |    25671459.61 |      77116505947
   500 |   7087810.72 |   130409933.31 |      77825129143
   600 |   7092043.09 |   145026362.85 |      78534213005
   700 |   7096275.47 |    55875753.40 |      79243699942
   800 |   7099357.28 |    92043120.29 |      79953547550
   900 |   7103325.97 |    60356235.71 |      80663694090
  1000 |   7116645.71 |   222333253.93 |      81374948735
  1100 |   7120625.09 |    81138380.12 |      82086862299
  1200 |   7133958.08 |   162412947.76 |      82799806138
  1300 |   7137944.96 |   226446344.72 |      83513378811
  1400 |   7152172.16 |   283834050.52 |      84228396696
  1500 |   7165546.40 |   273808268.36 |      84944790575
  1600 |   7169543.97 |   243586238.80 |      85661538713
  1700 |   7183799.17 |   205420431.73 |      86379647612
  1800 |   7197214.67 |    89354378.89 |      87098964170
  1900 |   7198380.27 |   381062040.76 |      87818746248
  2000 |   7215502.93 |   239434089.43 |      88539319882
  2100 |   7228692.80 |    47532844.16 |      89260949526
  2200 |   7228962.88 |   284797942.28 |      89983829339
  2300 |   7232981.84 |    19914908.04 |      90706814351
  2400 |   7247289.84 |   247750208.04 |      91430599007
  2500 |   7247293.04 |   468255454.84 |      92155328196
  2600 |   7260791.04 |    89371683.12 |      92881237927
  2700 |   7261964.16 |   249362258.20 |      93607356917
  2800 |   7264820.69 |   405795946.53 |      94333710443
  2900 |   7279156.69 |   563040127.87 |      95061296384
  3000 |   7292426.51 |    82957440.35 |      95789358296
  3100 |   7292699.15 |   169980900.73 |      96518607218
  3200 |   7467370.61 |   255189645.27 |      97253815962
  3300 |   7468547.49 |   350933166.08 |      98000607160
  3400 |   7474274.43 |   442717991.48 |      98747799798
  3500 |   7488638.43 |   535272254.15 |      99496247085
  3600 |   7488641.63 |   617300196.21 |     100245111190
  3700 |   7502378.08 |   644801830.41 |     100995142951
  3800 |   7502652.00 |   656504189.45 |     101745404590
  3900 |   7503832.64 |   658167276.13 |     102495772506
  4000 |   7509573.44 |   655331004.73 |     103246655220
  4100 |   7523965.44 |   653249083.73 |     103998850276
  4200 |   7523968.64 |   638784309.53 |     104751247089
  4300 |   7537752.00 |   561291496.17 |     105504663921
  4400 |   7538027.20 |   465740311.37 |     106258455908
  4500 |   7539211.60 |   358588145.17 |     107012314295
  4600 |   7544966.27 |   245916622.51 |     107766419604
  4700 |   7559386.27 |   133239865.17 |     108521161371
  4800 |   7559389.47 |     7287666.84 |     109277099998
  4900 |   7559389.47 |   763226613.51 |     110033038944
  5000 |   7573219.73 |   564642906.91 |     110790001331

--- End-of-Run Summary ---
Final CpS:                7573219.73
Total cookies baked:    110790001331
Total purchases:                 177
Upgrades purchased:                2
Avg ticks between purchases:     28.0
Real time:                    0.0s

Upgrades purchased:
  Cursor tier 5
  Factory tier 4

Buildings owned & CpS share:
  Cursor         owned:  129   CpS share:   0.0%
  Grandma        owned:  116   CpS share:   3.1%
  Farm           owned:   98   CpS share:   0.4%
  Mine           owned:   81   CpS share:   1.3%
  Factory        owned:   64   CpS share:   4.9%
  Bank           owned:   47   CpS share:   9.0%
  Temple         owned:   31   CpS share:  31.5%
  Wizard Tower   owned:   18   CpS share:  49.9%
  Shipment       owned:    0   CpS share:   0.0%
  Alchemy Lab    owned:    0   CpS share:   0.0%