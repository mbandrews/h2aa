#for full 2018 (Era2018_RR-17Sep2018_v2-legacyRun2FullV2-v0, rereco A-D dataset).  Trigger scale factors for use without HLT applied in MC
leadTriggerScaleBins =
    variables = cms.vstring("full5x5_r9","abs(superCluster.eta)","pt"),
    bins = cms.VPSet(

        ([0.0, 35.0, 37.0, 40.0, 45.0, 50.0, 60.0, 70.0, 90.0, 99999.])

                0.8020693032,
                0.9155469694,
                0.9266209669,
                0.9295708491,
                0.9303265907,
                0.9416725453,
                0.9503439663,
                0.9574423947,
                0.9523387414,
                #0 <eta < 1.5, R9<0.54 (cat 2 r9 turn-on bin)
                (0.0108370679,0.0108370679),
                (0.0042798703,0.0042798703),
                (0.0020932481,0.0020932481),
                (0.0012322936,0.0012322936),
                (0.0024324819,0.0024324819),
                (0.0057677517,0.0057677517),
                (0.0143137857,0.0143137857),
                (0.0120714856,0.0120714856),
                (0.0267745254,0.0267745254),

                0.8524002552,
                0.9476119412,
                0.9537999031,
                0.9606177455,
                0.9652220994,
                0.9677140340,
                0.9714560889,
                0.9792025583,
                0.9846367363,
                #0 <eta < 1.5, 0.54 < R9<0.85 (cat 2 r9 plateau-bin)
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0012234955,0.0012234955),
                (0.0021872047,0.0021872047),
                (0.0016488000,0.0016488000),

                0.8855419724,
                0.9599693694,
                0.9665558231,
                0.9729324583,
                0.9784734824,
                0.9806145301,
                0.9814731790,
                0.9830517669,
                0.9903382393,
                #0 <eta < 1.5, R9>0.85 (cat 0)
                (0.0010000000,0.0010000000),
                (0.0012218737,0.0012218737),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),

        )
    )

subleadTriggerScaleBins = 
    variables = cms.vstring("full5x5_r9","abs(superCluster.eta)","pt"),
    bins = cms.VPSet(

        ([0.0, 28.0, 31.0, 35.0, 40.0, 45.0, 50.0, 60.0, 70.0, 90.0, 999999])
                0.8884153471,
                0.9517603567,
                0.9690496396,
                0.9717160162,
                0.9796815413,
                0.9843574751,
                0.9844776733,
                0.9873999094,
                0.9933255120,
                0.9804395842,
                #0 <eta < 1.5, R9<0.54 (cat 2 r9 turn-on bin)
                (0.0035078397,0.0035078397),
                (0.0012683293,0.0012683293),
                (0.0014644761,0.0014644761),
                (0.0013420893,0.0013420893),
                (0.0010000000,0.0010000000),
                (0.0019132259,0.0019132259),
                (0.0040644219,0.0040644219),
                (0.0053801091,0.0053801091),
                (0.0063638347,0.0063638347),
                (0.0310825604,0.019560)

                0.9184639454,
                0.9950437401,
                0.9917999437,
                0.9939153322,
                0.9947390674,
                0.9945127334,
                0.9953081007,
                0.9968578311,
                0.9956645030,
                0.9957331016,
                #0 <eta < 1.5, 0.54<R9<0.85 (cat 2 r9 plateau bin)
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0024445012,0.0024445012),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),

                0.9482245748,
                0.9999020755,
                0.9999120130,
                0.9999573970,
                0.9999830622,
                0.9999880454,
                0.9999938661,
                0.9999867470,
                0.9999972153,
                0.9999550063,
                #0 <eta < 1.5, R9>0.85 (cat 0)
                (0.0024089227,0.0024089227),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0026996598,0.0026996598),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),
                (0.0010000000,0.0010000000),

        )
    )
