(
var output = "HYPERFRAMES_SFX_OUTPUT".getenv;
var kind = "HYPERFRAMES_SFX_KIND".getenv;
var duration = "HYPERFRAMES_SFX_DURATION".getenv.asFloat;
var seed = "HYPERFRAMES_SFX_SEED".getenv.asInteger;
var gain = "HYPERFRAMES_SFX_GAIN".getenv.asFloat;
var def, score;
thisThread.randSeed = seed;
def = SynthDef(\harnessSfx, {
    var sound, envelope;
    RandSeed.ir(1, seed);
    envelope = EnvGen.ar(Env.perc(0.004, duration - 0.04), doneAction: 2);
    sound = switch(kind,
        "click", { SinOsc.ar(XLine.ar(1500, 450, duration), 0, 0.4) },
        "whoosh", { BPF.ar(WhiteNoise.ar(0.7), XLine.ar(300, 7000, duration), 0.4) },
        "riser", { SinOsc.ar(XLine.ar(140, 2200, duration), 0, 0.25) + BPF.ar(WhiteNoise.ar(0.2), XLine.ar(400, 8000, duration), 0.3) },
        "fall", { SinOsc.ar(EnvGen.ar(Env([1600, 60, 260, 70, 130, 50],
            [0.45, 0.12, 0.18, 0.1, 0.15] * duration, \exp)), 0, 0.35) },
        "impact", { SinOsc.ar(XLine.ar(180, 35, 0.25), 0, 0.5) + LPF.ar(WhiteNoise.ar(0.3), 1600) }
    );
    if(kind == "riser" or: { kind == "whoosh" }, {
        envelope = EnvGen.ar(Env([0, 1, 0], [duration * 0.7, duration * 0.26], [2, -4]), doneAction: 2);
    });
    if(kind == "riser", {
        sound = (sound * envelope) + (LPF.ar(WhiteNoise.ar(0.5), 2200)
            * EnvGen.ar(Env([0, 0, 1, 0], [duration * 0.7, 0.004, duration * 0.26], [0, 0, -5])));
        envelope = 1;
    });
    OffsetOut.ar(0, (sound * envelope * gain).dup);
});
score = Score([[0, [\d_recv, def.asBytes]], [0, [\s_new, \harnessSfx, 1000, 0, 0]]]);
score.recordNRT(oscFilePath: output ++ ".osc", outputFilePath: output, sampleRate: 48000,
    headerFormat: "WAV", sampleFormat: "int16", options: ServerOptions.new.numOutputBusChannels_(2),
    duration: duration, action: { 0.exit });
)
