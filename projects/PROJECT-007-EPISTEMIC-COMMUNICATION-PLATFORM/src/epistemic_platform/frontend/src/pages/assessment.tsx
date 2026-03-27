import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAssessmentQuestions, useSubmitAssessment } from '@/hooks/use-api';
import { useAuthStore } from '@/stores/auth-store';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { ChevronRight, Brain, HelpCircle, ChevronDown, ChevronUp } from 'lucide-react';

interface Question {
  id: string;
  text: string;
  options: { key: string; text: string; stance_signal: string }[];
}

export function AssessmentPage() {
  const navigate = useNavigate();
  const { data, isLoading } = useAssessmentQuestions();
  const submitMutation = useSubmitAssessment();
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [step, setStep] = useState(0);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const updateUser = useAuthStore((s) => s.updateUser);

  const questions: Question[] = data?.questions ?? [];
  const total = questions.length;
  const current = questions[step];
  const allDone = Object.keys(answers).length === total && total > 0;

  const selectOption = (key: string) => {
    setAnswers((prev) => ({ ...prev, [current.id]: key }));
  };

  const next = () => {
    if (step < total - 1) setStep(step + 1);
  };

  const prev = () => {
    if (step > 0) setStep(step - 1);
  };

  const submit = async () => {
    const res = await submitMutation.mutateAsync({ answers });
    const resultData = res as Record<string, unknown>;
    setResult(resultData);
    // Update auth store so the Layout soft-gate opens
    const currentUser = useAuthStore.getState().user;
    if (currentUser) {
      updateUser({
        assessment_history: [...(currentUser.assessment_history || []), resultData as never],
      });
    }
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-2xl space-y-4 pt-12">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  // Results view
  if (result) {
    const stance = String(result.primary_stance ?? 'Unknown');
    const confidence = (Number(result.confidence) || 0) * 100;
    const stanceExplanations = (result.stance_explanations ?? {}) as Record<string, { name: string; short: string; description: string }>;
    const primaryInfo = stanceExplanations[stance] ?? null;
    const stanceName = primaryInfo?.name ?? stance.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase());
    const answerDeductions = (result.answer_deductions ?? []) as Array<{ question: string; your_answer: string; stance_signal: string; stance_name: string }>;
    const [showDeductions, setShowDeductions] = useState(false);

    return (
      <div className="mx-auto max-w-2xl space-y-6 pt-8">
        <div className="text-center space-y-2">
          <Brain className="mx-auto h-10 w-10 text-primary" />
          <h1 className="text-2xl font-bold">Your Reasoning Style</h1>
          <p className="text-muted-foreground">Here's what we discovered about how you approach knowledge</p>
        </div>

        {/* Primary stance card */}
        <Card className="border-primary/30">
          <CardContent className="pt-6 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xl font-bold">{stanceName}</span>
              <Badge>{Math.round(confidence)}% match</Badge>
            </div>
            {primaryInfo ? (
              <div className="space-y-2">
                <p className="text-sm font-medium text-primary">{primaryInfo.short}</p>
                <p className="text-sm text-muted-foreground leading-relaxed">{primaryInfo.description}</p>
              </div>
            ) : result.explanation ? (
              <p className="text-sm text-muted-foreground">{String(result.explanation)}</p>
            ) : null}
          </CardContent>
        </Card>

        {/* How we deduced this — collapsible */}
        {answerDeductions.length > 0 && (
          <Card>
            <CardHeader className="cursor-pointer" onClick={() => setShowDeductions(!showDeductions)}>
              <CardTitle className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2">
                  <HelpCircle className="h-4 w-4" /> How We Determined Your Profile
                </span>
                {showDeductions ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </CardTitle>
              <CardDescription className="text-xs">See which answers shaped your result — this helps you be more accurate next time</CardDescription>
            </CardHeader>
            {showDeductions && (
              <CardContent className="space-y-3 pt-0">
                {answerDeductions.map((d, i) => (
                  <div key={i} className="rounded-md border p-3 space-y-1">
                    <p className="text-xs text-muted-foreground">{d.question}</p>
                    <p className="text-sm">→ {d.your_answer}</p>
                    <Badge variant="outline" className="text-[10px]">{d.stance_name}</Badge>
                  </div>
                ))}
              </CardContent>
            )}
          </Card>
        )}

        {/* Stance distribution */}
        {result.stance_scores ? (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Your Stance Distribution</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(result.stance_scores as Record<string, number>)
                .sort(([, a], [, b]) => b - a)
                .map(([s, v]) => {
                  const info = stanceExplanations[s];
                  const label = info?.name ?? s.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase());
                  return (
                    <div key={s} className="space-y-0.5">
                      <div className="flex items-center gap-3">
                        <span className="w-36 text-xs text-muted-foreground">{label}</span>
                        <Progress value={v * 100} className="h-2 flex-1" />
                        <span className="text-xs text-muted-foreground w-10 text-right">{Math.round(v * 100)}%</span>
                      </div>
                    </div>
                  );
                })}
            </CardContent>
          </Card>
        ) : null}

        <Button className="w-full" onClick={() => navigate('/actors')}>
          Continue to Actors <ChevronRight className="ml-1 h-4 w-4" />
        </Button>
      </div>
    );
  }

  if (!current) return null;

  return (
    <div className="mx-auto max-w-2xl space-y-6 pt-8">
      <div className="text-center space-y-1">
        <h1 className="text-2xl font-bold">Epistemological Assessment</h1>
        <p className="text-sm text-muted-foreground">Answer a few questions so we can calibrate your coaching</p>
      </div>

      <div className="flex items-center gap-3">
        <Progress value={((step + 1) / total) * 100} className="h-2 flex-1" />
        <span className="text-xs text-muted-foreground whitespace-nowrap">{step + 1}/{total}</span>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{current.text}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {current.options.map((opt) => (
            <button
              key={opt.key}
              onClick={() => selectOption(opt.key)}
              className={`w-full rounded-md border px-4 py-3 text-left text-sm transition-colors ${
                answers[current.id] === opt.key
                  ? 'border-primary bg-primary/10 text-foreground'
                  : 'border-card-border bg-card hover:border-primary/50'
              }`}
            >
              <span className="mr-2 font-mono text-xs text-muted-foreground">{opt.key.toUpperCase()}.</span>
              {opt.text}
            </button>
          ))}
        </CardContent>
      </Card>

      <div className="flex justify-between">
        <Button variant="ghost" onClick={prev} disabled={step === 0}>
          Back
        </Button>
        {step < total - 1 ? (
          <Button onClick={next} disabled={!answers[current.id]}>
            Next <ChevronRight className="ml-1 h-4 w-4" />
          </Button>
        ) : (
          <Button onClick={submit} disabled={!allDone || submitMutation.isPending}>
            {submitMutation.isPending ? 'Evaluating…' : 'Submit'}
          </Button>
        )}
      </div>
    </div>
  );
}
