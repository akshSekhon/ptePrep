import { useEffect, useRef, useState } from "react";
import { Check, Headphones, LoaderCircle, Mic2, Play, Square, Volume2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function DeviceCheck({ needsMicrophone, onReady }: { needsMicrophone: boolean; onReady: () => void }) {
  const recorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);
  const stream = useRef<MediaStream | null>(null);
  const audioContext = useRef<AudioContext | null>(null);
  const playbackUrl = useRef("");
  const [recording, setRecording] = useState(false);
  const [recordedUrl, setRecordedUrl] = useState("");
  const [micError, setMicError] = useState("");
  const [speakerTested, setSpeakerTested] = useState(false);
  useEffect(() => () => { if (recorder.current?.state === "recording") recorder.current.stop(); stream.current?.getTracks().forEach((track) => track.stop()); if (audioContext.current) void audioContext.current.close(); if (playbackUrl.current) URL.revokeObjectURL(playbackUrl.current); }, []);
  const startMic = async () => {
    try {
      stream.current = await navigator.mediaDevices.getUserMedia({ audio: true });
      const type = MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : undefined;
      const active = type ? new MediaRecorder(stream.current, { mimeType: type }) : new MediaRecorder(stream.current);
      chunks.current = [];
      active.ondataavailable = (event) => { if (event.data.size) chunks.current.push(event.data); };
      active.onstop = () => { stream.current?.getTracks().forEach((track) => track.stop()); if (playbackUrl.current) URL.revokeObjectURL(playbackUrl.current); playbackUrl.current = URL.createObjectURL(new Blob(chunks.current, { type: type ?? "audio/webm" })); setRecordedUrl(playbackUrl.current); };
      active.start(); recorder.current = active; setMicError(""); setRecording(true);
    } catch { setMicError("The browser could not start a microphone recording. Check that this site is allowed to use your microphone and close any other app using it."); }
  };
  const stopMic = () => { recorder.current?.stop(); recorder.current = null; setRecording(false); };
  const testSpeaker = () => { if (audioContext.current) void audioContext.current.close(); const context = new AudioContext(); audioContext.current = context; const oscillator = context.createOscillator(); const gain = context.createGain(); oscillator.connect(gain); gain.connect(context.destination); gain.gain.setValueAtTime(0.05, context.currentTime); oscillator.start(); oscillator.stop(context.currentTime + 0.35); oscillator.onended = () => { void context.close(); audioContext.current = null; setSpeakerTested(true); }; };
  const ready = speakerTested && (!needsMicrophone || Boolean(recordedUrl));
  return <div className="mx-auto max-w-3xl space-y-6 animate-rise" data-testid="device-check-page"><div><div className="label-mono text-teal-700">Before your test</div><h1 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-950" data-testid="device-check-title">Check your microphone and sound</h1><p className="mt-2 text-sm leading-relaxed text-slate-500">Record a short sample, listen to it back, and confirm that you can hear the sound check before starting.</p></div><div className="grid gap-5 md:grid-cols-2"><section className="rounded-xl border border-slate-200 bg-white p-5" data-testid="microphone-check-card"><div className="flex items-center gap-3"><span className="flex size-10 items-center justify-center rounded-full bg-teal-100 text-teal-700"><Mic2 size={18} /></span><div><div className="font-bold text-slate-900">Microphone check</div><div className="text-xs text-slate-500">Say: “I am ready for my PTE practice test.”</div></div></div><div className="mt-5">{recording ? <Button variant="destructive" onClick={stopMic} data-testid="device-check-stop-recording"><Square size={15} /> Stop sample</Button> : <Button onClick={startMic} data-testid="device-check-record-button"><Mic2 size={15} /> Record sample</Button>}</div>{micError && <div className="mt-4 rounded-lg bg-rose-50 p-3 text-xs leading-relaxed text-rose-800" data-testid="device-check-mic-error">{micError}</div>}{recordedUrl && <div className="mt-4 space-y-3" data-testid="device-check-recording-ready"><audio controls src={recordedUrl} className="w-full" data-testid="device-check-recording-playback" /><div className="flex items-center gap-2 text-xs font-bold text-teal-700"><Check size={14} /> Recording captured—play it back to check your voice is clear.</div></div>}</section><section className="rounded-xl border border-slate-200 bg-white p-5" data-testid="speaker-check-card"><div className="flex items-center gap-3"><span className="flex size-10 items-center justify-center rounded-full bg-indigo-100 text-indigo-700"><Headphones size={18} /></span><div><div className="font-bold text-slate-900">Sound check</div><div className="text-xs text-slate-500">Use headphones for clearer listening practice.</div></div></div><Button className="mt-5" variant="outline" onClick={testSpeaker} data-testid="device-check-sound-button"><Volume2 size={15} /> Play sound check</Button>{speakerTested && <div className="mt-4 flex items-center gap-2 text-xs font-bold text-teal-700" data-testid="device-check-sound-ready"><Check size={14} /> Sound check played. If you heard it, your output is ready.</div>}</section></div><Button className="w-full" disabled={!ready} onClick={onReady} data-testid="device-check-continue-button">{ready ? <><Play size={15} /> Continue to test</> : <><LoaderCircle size={15} /> Complete the checks to continue</>}</Button></div>;
}