import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';

export default function Index() {
  const [step, setStep] = useState<'form' | 'payment'>('form');
  const [nickname, setNickname] = useState('');
  const [amount, setAmount] = useState('');
  const { toast } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!nickname || !amount) {
      toast({
        title: 'Ошибка',
        description: 'Заполните все поля',
        variant: 'destructive',
      });
      return;
    }
    setStep('payment');
  };

  const handlePayment = async () => {
    try {
      const response = await fetch('https://functions.poehali.dev/fd800dc4-3a7e-4679-9120-804c85a4ef8d', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          nickname,
          amount: parseInt(amount),
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        toast({
          title: '✅ Заявка отправлена',
          description: `Данные отправлены администратору в Telegram. Ожидайте начисления ${amount} донат рублей на ник ${nickname}`,
        });
      } else {
        toast({
          title: 'Ошибка',
          description: data.error || 'Не удалось отправить заявку',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Ошибка подключения',
        description: 'Проверьте интернет соединение',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-8 items-center">
        <div className="text-center lg:text-left space-y-6 animate-fade-in">
          <div className="flex items-center justify-center lg:justify-start gap-3">
            <div className="w-16 h-16 bg-primary rounded-xl flex items-center justify-center">
              <Icon name="Gamepad2" size={32} className="text-white" />
            </div>
            <h1 className="text-4xl lg:text-5xl font-bold text-secondary">SAMP Донат</h1>
          </div>
          <p className="text-lg text-muted-foreground max-w-lg">
            Быстрое пополнение донат рублей для вашего аккаунта. Простая и безопасная система оплаты.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
            <div className="flex items-center gap-2 text-sm">
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <Icon name="Zap" size={16} className="text-primary" />
              </div>
              <span className="text-muted-foreground">Моментальное зачисление</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <Icon name="Shield" size={16} className="text-primary" />
              </div>
              <span className="text-muted-foreground">Безопасная оплата</span>
            </div>
          </div>
        </div>

        <Card className="w-full animate-enter shadow-xl border-2">
          {step === 'form' ? (
            <>
              <CardHeader className="space-y-1">
                <CardTitle className="text-2xl flex items-center gap-2">
                  <Icon name="User" size={24} className="text-primary" />
                  Данные для доната
                </CardTitle>
                <CardDescription>
                  Введите ваш игровой ник и сумму пополнения
                </CardDescription>
              </CardHeader>
              <form onSubmit={handleSubmit}>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="nickname">Игровой ник</Label>
                    <div className="relative">
                      <Input
                        id="nickname"
                        placeholder="Введите ваш ник"
                        value={nickname}
                        onChange={(e) => setNickname(e.target.value)}
                        className="pl-10"
                      />
                      <Icon name="AtSign" size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="amount">Сумма (донат рублей)</Label>
                    <div className="relative">
                      <Input
                        id="amount"
                        type="number"
                        placeholder="100"
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                        className="pl-10"
                        min="1"
                      />
                      <Icon name="Coins" size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                    </div>
                  </div>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-2">
                    <div className="flex items-center gap-2">
                      <Icon name="Info" size={16} className="text-primary" />
                      <span className="text-sm font-medium text-primary">Информация</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      После оплаты данные автоматически отправятся администратору, и донат рубли будут зачислены на ваш аккаунт.
                    </p>
                  </div>
                </CardContent>
                <CardFooter>
                  <Button type="submit" className="w-full text-lg h-12" size="lg">
                    Продолжить
                    <Icon name="ArrowRight" size={20} className="ml-2" />
                  </Button>
                </CardFooter>
              </form>
            </>
          ) : (
            <>
              <CardHeader className="space-y-1">
                <CardTitle className="text-2xl flex items-center gap-2">
                  <Icon name="CreditCard" size={24} className="text-primary" />
                  Оплата
                </CardTitle>
                <CardDescription>
                  Переведите средства на указанную карту
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="bg-secondary text-white rounded-xl p-6 space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm opacity-80">Номер карты</span>
                    <Icon name="Copy" size={16} className="opacity-60 cursor-pointer hover:opacity-100 transition-opacity" />
                  </div>
                  <p className="text-2xl font-mono tracking-wider">2200 7020 5523 2552</p>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between p-3 bg-muted rounded-lg">
                    <span className="text-muted-foreground">Игровой ник:</span>
                    <span className="font-semibold">{nickname}</span>
                  </div>
                  <div className="flex justify-between p-3 bg-muted rounded-lg">
                    <span className="text-muted-foreground">Сумма к оплате:</span>
                    <span className="font-semibold text-primary">{amount} ₽</span>
                  </div>
                </div>

                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-2">
                  <div className="flex items-center gap-2">
                    <Icon name="AlertCircle" size={16} className="text-amber-600" />
                    <span className="text-sm font-medium text-amber-900">Важно</span>
                  </div>
                  <p className="text-sm text-amber-800">
                    После перевода нажмите кнопку "Я оплатил". Данные автоматически отправятся администратору в Telegram.
                  </p>
                </div>
              </CardContent>
              <CardFooter className="flex-col gap-3">
                <Button onClick={handlePayment} className="w-full text-lg h-12" size="lg">
                  <Icon name="Check" size={20} className="mr-2" />
                  Я оплатил
                </Button>
                <Button onClick={() => setStep('form')} variant="ghost" className="w-full">
                  <Icon name="ArrowLeft" size={16} className="mr-2" />
                  Назад
                </Button>
              </CardFooter>
            </>
          )}
        </Card>
      </div>
    </div>
  );
}