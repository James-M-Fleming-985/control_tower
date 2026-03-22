import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAssessmentQuestions, useSubmitAssessment } from '@/hooks/use-api';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { ChevronRight, Brain } from 'lucide-react';

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
    setResult(res as Record<string, unknown>);
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
    return (
      <div className="mx-auto max-w-2xl space-y-6 pt-8">
        <div className="text-center space-y-2">
          <Brain className="mx-auto h-10 w-10 text-primary" />
          <h1 className="text-2xl font-bold">Your Epistemological Profile</h1>
          <p className="text-muted-foreground">Here's what we discovered about your reasoning style</p>
        </div>
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-lg font-semibold capitalize">{stance}</span>
              <Badge>{Math.round(confidence)}% confidence</Badge>
            </div>
            {result.explanation ? (
              <p className="text-sm text-muted-foreground">{String(result.explanation)}</p>
            ) : null}
            {result.stance_scores ? (
              <div className="space-y-2 pt-2">
                {Object.entries(result.stance_scores as Record<string, number>).map(([s, v]) => (
                  <div key={s} className="flex items-center gap-3">
                    <span className="w-28 text-xs capitalize text-muted-foreground">{s}</span>
                    <Progress value={v * 100} className="h-2 flex-1" />
                    <span className="text-xs text-muted-foreground w-10 text-right">{Math.round(v * 100)}%</span>
                  </div>
                ))}
              </div>
            ) : null}
          </CardContent>
        </Card>
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
