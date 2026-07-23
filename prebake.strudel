// Prebake script
//
// This is code that is loaded before your pattern is run.
// You can use it to define custom functions to use in any pattern.
// 
// This is an initial example script. You can edit it to add 
// your own funtions.
//
// To use a script shared by some other user you can use
// the import-button or paste the script in this editor.

const ratchet = register('ratchet', (pat) => pat.sometimes(ply(3)))

register('slideTo', (semitones, pat) => 
  pat.penv(semitones).panchor(0)
)

register('slideFrom', (semitones, pat) => 
  pat.penv(-semitones).panchor(1)
)

function ensureMidiNote(note) {
    if (typeof note === 'string') {
      note = noteToMidi(note);
    }
  return note
}

register('glide', function (time, pat) {
  let prevNote = null;
  
  const query = (state) => {
    const haps = pat.query(state);
  
    const new_haps = []
    for (var i = 0; i < haps.length; i++) {
      let hap = haps[i]

      let note = ensureMidiNote(hap.value.note)
  
      let difference = 0
      if (prevNote != null) {
        difference = note - prevNote;
      }
      prevNote = note
  
      let newVal = hap.value;
      newVal = {
        ...hap.value,
        panchor: 1,
        penv: difference,
        pattack: time,
      }
  
      hap.value = newVal
      new_haps.push(
        new Hap(hap.whole, hap.part, newVal, hap.context)
      );
    }
    return new_haps
  };
  return new Pattern(query);
});


register('click', function (amt, pat) {
  if(amt > 0) {
    return pat.slideFrom(amt * 60).pattack(0.015) 
    
  } else {
    return  pat
  }
});

register('print_haps', function (pat) {
  const haps = pat.queryArc(0, 1);
  console.log(haps.map((e) => e.show()));
  return pat;
});

register('maskUntilNext', (grid, pat) => {
  const t = getTime();
  const qt = Math.ceil(t / grid) * grid;
  return pat.filterWhen((t) => t >= qt);
});

window.oneshot = register('oneshot', (grid, pat) => {
  const t = getTime();
  const qt = Math.ceil(t / grid) * grid;
  return pat.filterWhen((t) => t >= qt && t < qt + 1);
});


window.automate = register('automate', function (pat) {
  return new Pattern((state) => {
    const haps = []
    for (const hap of pat.queryArc(state.span.begin, state.span.end)) {
      if (Array.isArray(hap.value)) {
        const start = hap.whole.begin.valueOf()
        const end = hap.whole.end.valueOf()
        const a = hap.value[0]
        const b = hap.value[1]
  
        const progress = (state.span.begin - start) / (end - start)
        haps.push(new Hap(hap.whole, hap.part, a + (b - a) * progress, hap.context))
      } else {
        haps.push(hap)
      }
    }
    return haps
  })
})

// chord by root
const memo = (fn) => {
  const cache = new Map();
  return (...args) => {
    const k = args.join('|');
    if (!cache.has(k)) cache.set(k, fn(...args));
    return cache.get(k);
  };
};

const deg2note = memo((deg, sc) => pure(deg).scale(pure(sc)).queryArc(0, 1)[0].value);
const pc = (note) => note.match(/^[A-G][#b]*/)[0];
const accVal = (s) => [...s].reduce((a, c) => a + (c === 'b' ? -1 : 1), 0);

// parses b6 into degree 6 / alt -1, #4 or s4 into degree 4 / alt +1
const parseDegree = (v) => {
  const m = String(v).match(/^([#bs]*)(-?\d+)$/);
  if (!m) throw new Error('chordDegree: cannot parse degree ' + v);
  return [Number(m[2]), accVal(m[1].split('s').join('#'))];
};

// shift a pitch class by semitones, keeping the letter (B down 1 -> Bb, D# down 1 -> D)
const alterPc = (p, alt) => {
  const [, letter, accs] = p.match(/^([A-G])([#b]*)$/);
  const n = accVal(accs) + alt;
  return letter + (n >= 0 ? '#'.repeat(n) : 'b'.repeat(-n));
};

const triadSymbol = memo((deg, sc) => {
  const m = (n) => noteToMidi(deg2note(n, sc));
  const [third, fifth] = [m(deg + 2) - m(deg), m(deg + 4) - m(deg)];
  if (third === 4 && fifth === 7) return '';
  if (third === 3 && fifth === 7) return 'm';
  if (third === 3 && fifth === 6) return 'o';
  if (third === 4 && fifth === 8) return 'aug';
  return third <= 3 ? 'm' : '';
});

register('chordDegree', (sc, pat) => {
  if (Array.isArray(sc)) sc = sc.flat().join(' ');
  return pat.fmap((value) => {
    let symbol;
    if (Array.isArray(value)) [value, symbol] = value;
    else if (value && typeof value === 'object') value = value.n ?? value.note ?? value.value;
    const [deg, alt] = parseDegree(value);
    const root = alterPc(pc(deg2note(deg, sc)), alt);
    const sym = symbol ?? (alt ? (alt < 0 ? '' : 'o') : triadSymbol(deg, sc));
    return { chord: root + sym };
  });
});

register('widen', (amt, pat) => 
  pat.layer(
    pat=>pat.pan(0.5 + (amt/2)),
    pat=>pat.pan(0.5 - (amt/2)).late(0.001)
  ).postgain(0.8)
)

register('transposeSamplePreserve', (semitones, pat) => {
  const p = 2 ** (semitones / 12);              // desired frequency ratio
  return pat.stretch(p >= 1 ? p - 1 : 4 * (p - 1));
});

register('transposeSample', (semitones, pat) =>
  pat.mul(speed(2 ** (semitones / 12)))
);

//Distort makeup gain
const distGain = (d, A = 0.5, algo = 'scurve', N = 2048) => {
  const k = Math.expm1(d), f = distortionAlgorithms[algo];
  let ms = 0;
  for (let i = 0; i < N; i++) ms += f(A * Math.sin(2 * Math.PI * i / N), k) ** 2;
  const makeup = (A / Math.SQRT2) / Math.sqrt(ms / N);
  return Math.min(1, makeup); // worklet clamps postgain to ≤ 1 anyway
};

// wrap it so you never think about it again
// renamed to avoid clobbering the built-in `dist` alias
const distRect = register('distRect', (d, pat) => pat.distort(d).distortvol(distGain(d)));

register('white', (level, pat) => 
  stack(pat, s("white").gain(level).struct(pat).clip(1))
)
