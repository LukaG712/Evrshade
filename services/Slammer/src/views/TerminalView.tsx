// Terminal view — interactive command terminal

import { useState, useEffect, useRef } from 'react';

export default function TerminalView() {
  const [lines, setLines] = useState<string[]>(['Evershade Terminal — Connected', 'Type "help" for available commands.', '']);
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [lines]);

  const clickToFocus = () => inputRef.current?.focus();

  const executeCommand = (cmd: string) => {
    const trimmed = cmd.trim().toLowerCase();
    const newLines = [...lines, `> ${cmd}`];

    switch (trimmed) {
      case 'help':
        newLines.push(
          'Available commands:',
          '  help          — Show this help message',
          '  status        — Show service status',
          '  agents        — List agents',
          '  missions      — List missions',
          '  tasks         — List tasks',
          '  clear         — Clear terminal',
          '  version       — Show version',
          ''
        );
        break;
      case 'status':
        newLines.push(
          'Services:',
          '  Greenie       — Agent orchestration',
          '  Slinker       — Code execution',
          '  Trapper       — Browser automation',
          '  Gobber        — Memory & storage',
          '  Sneaker       — Observability',
          '  Hider         — Secrets management',
          '  Poltergeist   — Notifications',
          '  Shrewd        — LLM routing',
          '  Slammer       — Dashboard (this)',
          '  Speedy        — CLI tool',
          ''
        );
        break;
      case 'agents':
        newLines.push('Use the Agents tab or run: evershade agents');
        break;
      case 'missions':
        newLines.push('Use the Missions tab or run: evershade missions');
        break;
      case 'tasks':
        newLines.push('Use the Tasks tab or run: evershade tasks');
        break;
      case 'clear':
        setLines(['']);
        return;
      case 'version':
        newLines.push('Evershade v2.0.0');
        break;
      case '':
        break;
      default:
        newLines.push(`Unknown command: ${trimmed}. Type "help" for available commands.`);
    }

    setLines(newLines);
    if (trimmed) setHistory(prev => [cmd, ...prev]);
    setHistoryIndex(-1);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeCommand(input);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (history.length > 0 && historyIndex < history.length - 1) {
        const newIndex = historyIndex + 1;
        setHistoryIndex(newIndex);
        setInput(history[newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setInput(history[newIndex]);
      } else {
        setHistoryIndex(-1);
        setInput('');
      }
    }
  };

  return (
    <div className="space-y-4" onClick={clickToFocus}>
      <div className="bg-gray-950 rounded-lg border border-gray-700 p-4 font-mono text-sm">
        <div className="max-h-[500px] overflow-y-auto">
          {lines.map((line, i) => (
            <div key={i} className="text-gray-300 whitespace-pre-wrap">{line}</div>
          ))}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={handleSubmit} className="flex items-center gap-2 mt-2">
          <span className="text-green-400">❯</span>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 bg-transparent outline-none text-gray-100"
            autoFocus
            spellCheck={false}
          />
        </form>
      </div>

      <p className="text-xs text-gray-500">
        Tip: For full CLI functionality, use the Speedy CLI tool: <code className="bg-gray-800 px-1 rounded">evershade status</code>
      </p>
    </div>
  );
}
