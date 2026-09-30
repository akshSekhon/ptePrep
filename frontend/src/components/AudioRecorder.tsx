import { useRef, useState } from "react";
import { LoaderCircle, Mic2, Square, Volume2 } from "lucide-react";
import { apiUpload } from "@/lib/api";
import type { AudioTranscript } from "@/lib/pte";

interface AudioRecorderProps {
  onTranscript: (transcript: string, duration: number) => void;
  onError: (message: string) => void;
  onPermissionChange?: (granted: boolean) => void;
}

export default function AudioRecorder({ onTranscript, onError, onPermissionChange }: AudioRecorderProps) {
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const startedAtRef = useRef(0);
  const [recording, setRecording] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [permissionDenied, setPermissionDenied] = useState(false);

  const startRecording = async () => {
    try {
      if (!navigator.mediaDevices?.getUserMedia) throw new Error("Microphone recording is not supported in this browser");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setPermissionDenied(false);
      onPermissionChange?.(true);
      const mime = MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "audio/mp4";
      const recorder = new MediaRecorder(stream, { mimeType: mime });
      chunksRef.current = [];
      startedAtRef.current = Date.now();
      recorder.ondataavailable = (event) => { if (event.data.size) chunksRef.current.push(event.data); };
      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        const duration = Math.max(1, Math.round((Date.now() - startedAtRef.current) / 1000));
        setElapsed(duration);
        setTranscribing(true);
        try {
          const extension = mime.includes("mp4") ? "m4a" : "webm";
          const formData = new FormData();
          formData.append("file", new Blob(chunksRef.current, { type: mime }), `pte-response.${extension}`);
          const result = await apiUpload<AudioTranscript>("/pte/transcribe", formData);
          onTranscript(result.transcript, duration);
        } catch {
          onError("Transcription could not be completed. You can still type your response below.");
        } finally {
          setTranscribing(false);
        }
      };
      recorder.start();
      recorderRef.current = recorder;
      setElapsed(0);
      setRecording(true);
    } catch {
      setPermissionDenied(true);
      onPermissionChange?.(false);
      onError("Microphone access is required for speaking practice. Enable it in your browser, then try again.");
    }
  };

  const stopRecording = () => {
    recorderRef.current?.stop();
    recorderRef.current = null;
    setRecording(false);
  };

  return (
    <div className="rounded-xl border border-teal-200 bg-teal-50/70 p-4" data-testid="audio-recorder">
      <div className="flex items-center gap-3"><div className={`flex size-10 items-center justify-center rounded-full ${recording ? "bg-rose-100 text-rose-600" : "bg-teal-100 text-teal-700"}`}><Mic2 size={18} /></div><div><div className="text-sm font-bold text-slate-800" data-testid="audio-recorder-title">{recording ? "Recording response" : transcribing ? "Transcribing response" : "Record your response"}</div><div className="mt-1 text-xs text-slate-500" data-testid="audio-recorder-status">{recording ? `${elapsed}s · speak clearly and keep a steady pace` : transcribing ? "Whisper is turning your recording into text..." : "Browser microphone → Whisper transcription → AI feedback"}</div></div>{transcribing ? <LoaderCircle className="ml-auto animate-spin text-teal-600" size={18} /> : <Volume2 className="ml-auto text-teal-500" size={18} />}</div>
      <div className="mt-4 flex items-center gap-3">{recording ? <button type="button" className="inline-flex items-center gap-2 rounded-lg bg-rose-600 px-3 py-2 text-xs font-bold text-white transition-[background-color,transform] hover:bg-rose-700 active:translate-y-px" onClick={stopRecording} data-testid="stop-recording-button"><Square size={13} fill="currentColor" /> Stop recording</button> : <button type="button" disabled={transcribing} className="inline-flex items-center gap-2 rounded-lg bg-teal-700 px-3 py-2 text-xs font-bold text-white transition-[background-color,transform] hover:bg-teal-800 disabled:opacity-50 active:translate-y-px" onClick={startRecording} data-testid="start-recording-button"><Mic2 size={13} /> Enable microphone & record</button>}<span className="text-[11px] text-slate-400" data-testid="audio-recorder-duration">{elapsed ? `${elapsed}s captured` : "No recording yet"}</span></div>
      {permissionDenied && <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs leading-relaxed text-amber-900" data-testid="microphone-permission-help"><strong>Microphone blocked.</strong> Select the lock or microphone icon beside your browser address bar, allow microphone access for this site, then press “Enable microphone & record” again. Speaking answers cannot be submitted as typed text.</div>}
    </div>
  );
}