let v = sound "psr"


--- ========================
-- init, OBSOLETE -- dupd to TidalCustom.hs, nicer there
  -- functions
    let dur = cps . (\x -> 1 / x)
    let hi = speed . ((step**) <$>) where step = 2**(1/31)
    let hi_ob transp = speed . ((step**) . (+ transp) <$>) where step = 2**(1/31) 
    -- rotl :: Int -> [a] -> [a]
    let rotl n xs = take (length xs) . drop n . cycle $ xs
  --scales
    let sDia = [ 0, 5, 10, 13, 18, 23, 28] :: [Double]
    let sMel = [ 0, 5, 10, 15, 20, 23, 28] :: [Double]
    let sHar = [ 0, 5, 10, 13, 20, 23, 28] :: [Double]
    let sAnt = [ 0, 5, 10, 13, 18, 21, 28] :: [Double]
  -- harmonics: 10 (5/4), 14 (11/8), 18 (3/2), 22 (13/8), 25 (7/4)
  -- tuning(in 31et) to jvbass
    let psrCorr = (+1.82) -- psr correction, to harmonize jvbass
      -- to prove that correction
      -- d1 $ sound "psr*4" |+| up "1.82"
      -- d2 $ (1/8) <~ sound "jvbass*4"
    let fCorr = (+ 7.0)
      -- let fcorr = (+ 7)
      -- d1 $ sound "jvbass*3" |+| pit 0 "0"
      -- d2 $ sound "f" |+| gain "0.7" |+| pit (fcorr 0) "0"
  -- scales!
    let remPos num den = if x<0 then x+den else x where x = rem num den
    -- fmap (flip remPos 3) [-5..5] -- positive remainder (works)
    -- scaleElt :: [Double] -> Int -> Double
    let scaleElt scale n = fromIntegral .(scale !!) $ fromIntegral $ remPos n (fromIntegral $ length scale) 
    -- fmap (scaleElt [0,3,7]) [-5..5] --test
    -- scaleOctave :: [Double] -> Int -> Double -- type sig breaks it
    let scaleOctave scale n = (31 *) . fromIntegral . floor . ((fromIntegral n) /) $ fromIntegral $ length scale  
    -- fmap (scaleOctave s) [-1..1] --test
    -- fmap (scaleOctave s) [-5..5] --test
    let scale s n = scaleOctave s n + scaleElt s n 
    -- scale s 1
    -- fmap (scale s) [-1..1]
  -- synonyms
    let fast = density
    let cyc = slowspread
-- challenge-reminders!
  -- permanent gradual|scheduled changes!


-- ================ FROM HERE ON I think it's garbage

-- copied from longfunc.tidal for 12et, share 
  let s = [0,3,7]

  let remPos num den = if x < 0 then x + den else x where x = rem num den -- test (works): fmap (flip remPos 3) [-5..5]
  let fStep = \scale n -> (scale !!) $ fromIntegral $ remPos n (fromIntegral $ length scale) -- test (works): fmap (fStep [0,3,7]) [-5..5]
    -- adding this type sig breaks it :: [Double] -> Int  -> Double
  let fOct scale n = (12 *) . floor . (n /) $ fromIntegral $ length scale -- test (works): fmap (fOct s) [-1..1] ++ fmap (fOct s) [-5..5]
  scale' s n = fromIntegral $ scaleScaleSummand s n + scaleOctaveSummand s n


let remPos num den = if x < 0 then x + den else x where x = rem num den
let fStep scale n = (scale !!) $ fromIntegral $ remPos n (fromIntegral $ length scale) -- scaleScaleSummand
  fmap (fStep [0,4,7]) [-5..5] -- test (success)
let fOct scale n = fromIntegral $ (31 *) . floor . (n /) $ fromIntegral $ length scale -- scaleOctaveSummand 
let scale' s n = fStep s n + fOct s n

-- this is experimental (type sigs) copy of prev parag
let remPos num den = if x < 0 then x + den else x where x = rem num den
let fStep = \scale n -> (scale !!) $ bfromIntegral $ remPos n (fromIntegral $ length scale) :: -> [Double] -> Int -> Double
let fOct = \scale n -> (31 *) . floor . (n /) $ fromIntegral $ length scale :: [Double] -> Int -> Double
let scale' s n = fStep s n + fOct s n

let f = (\x y -> x + y) :: Double -> Double -> Double -- try type sigs next --RESUME HERE (is middle, relevant to both sides)

--  above paragraph works, below paragraph doesn't
let scale s = ((scale' s) <$>) -- :: ? Pattern Int -> Pattern Double
scale [10..14] ("1 2" :: Pattern Int) -- ? :: Pattern Double



let scaleIndex scale n = (scale !!) $ fromIntegral $ floor $ n / length scale

floor $ x / y
rem num den

(+ 1) <$> ("1 2" :: Pattern Double)

