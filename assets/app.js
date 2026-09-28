(() => {
  const sidebar = document.querySelector('.site-sidebar');
  const toggle = document.querySelector('.sidebar-toggle');
  const backdrop = document.querySelector('.sidebar-backdrop');
  const groups = [...document.querySelectorAll('[data-nav-group]')];
  const mobile = matchMedia('(max-width:760px)');
  const setGroup = (group, open) => {
    group.querySelector('.submenu-toggle').setAttribute('aria-expanded', String(open));
    group.querySelector('.nav-contents').hidden = !open;
  };
  const openGroup = group => groups.forEach(other => setGroup(other, other === group));
  const closeMenu = () => {
    sidebar.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open navigation');
    backdrop.hidden = true;
    document.body.style.overflow = '';
    groups.forEach(group => setGroup(group, false));
  };
  groups.forEach(group => {
    const button = group.querySelector('.submenu-toggle');
    group.addEventListener('pointerenter', event => {
      if (event.pointerType === 'mouse' && !mobile.matches) openGroup(group);
    });
    group.addEventListener('pointerleave', () => {
      if (!group.contains(document.activeElement)) setGroup(group, false);
    });
    group.addEventListener('focusin', event => {
      if (!mobile.matches && event.target !== button) openGroup(group);
    });
    group.addEventListener('focusout', event => {
      if (!group.contains(event.relatedTarget)) setGroup(group, false);
    });
    button.addEventListener('click', () => {
      const opening = button.getAttribute('aria-expanded') !== 'true';
      groups.forEach(other => setGroup(other, other === group && opening));
    });
  });
  toggle.addEventListener('click', () => {
    const open = !sidebar.classList.contains('open');
    closeMenu();
    if (open) {
      sidebar.classList.add('open');
      toggle.setAttribute('aria-expanded', 'true');
      toggle.setAttribute('aria-label', 'Close navigation');
      backdrop.hidden = false;
      document.body.style.overflow = 'hidden';
    }
  });
  backdrop.addEventListener('click', closeMenu);
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      if (sidebar.classList.contains('open')) { closeMenu(); toggle.focus(); }
      else {
        const open = groups.find(group => group.querySelector('.submenu-toggle').getAttribute('aria-expanded') === 'true');
        if (open) { setGroup(open, false); open.querySelector('.submenu-toggle').focus(); }
      }
    }
    if (event.key === 'Tab' && sidebar.classList.contains('open')) {
      const focusable = [...sidebar.querySelectorAll('a, button')].filter(el => el.getClientRects().length);
      const first = focusable[0], last = focusable.at(-1);
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });
  if (typeof mobile.addEventListener === 'function') mobile.addEventListener('change', closeMenu);
  else mobile.addListener(closeMenu);

  const journal = document.querySelector('[data-journal]');
  if (journal) {
    let category = 'all';
    const input = journal.querySelector('[data-search-input]');
    const cards = [...journal.querySelectorAll('[data-post]')];
    const buttons = [...journal.querySelectorAll('[data-filter]')];
    const refresh = () => {
      const query = input.value.trim().toLowerCase();
      let count = 0;
      cards.forEach(card => {
        const match = (category === 'all' || card.dataset.category === category) &&
          query.split(/\s+/).every(word => card.dataset.search.includes(word));
        card.hidden = !match;
        if (match) count++;
      });
      buttons.forEach(button => {
        const active = button.dataset.filter === category;
        button.classList.toggle('active', active);
        button.setAttribute('aria-pressed', String(active));
      });
      journal.querySelector('[data-empty]').hidden = count !== 0;
      journal.querySelector('[data-search-status]').textContent = `${count} ${count === 1 ? 'article' : 'articles'}.`;
    };
    buttons.forEach(button => button.addEventListener('click', () => { category = button.dataset.filter; refresh(); }));
    input.addEventListener('input', refresh);
    journal.querySelector('[data-reset]').addEventListener('click', () => { category = 'all'; input.value = ''; refresh(); input.focus(); });
    refresh();
  }

  const directory = document.querySelector('[data-project-directory]');
  if (directory) {
    const buttons = [...directory.querySelectorAll('[data-project-filter]')];
    buttons.forEach(button => button.addEventListener('click', () => {
      const environment = button.dataset.projectFilter;
      let count = 0;
      directory.querySelectorAll('[data-project]').forEach(card => {
        card.hidden = environment !== 'all' && card.dataset.environment !== environment;
        if (!card.hidden) count++;
      });
      buttons.forEach(other => {
        other.classList.toggle('active', other === button);
        other.setAttribute('aria-pressed', String(other === button));
      });
      const text = `${count} ${count === 1 ? 'project' : 'projects'}`;
      directory.querySelector('[data-project-count]').textContent = text;
      directory.querySelector('[data-project-status]').textContent = text;
    }));
  }

  const example = document.querySelector('[data-primitive-example]');
  if (example) {
    const reference = example.querySelector('[data-primitive-links] a').href.split('#')[0];
    const stages = {
      read: { title: 'Read the board and select a legal move', description: 'Validate permitted inputs, reconstruct the visible board and tokens, then use explicit game logic to select a legal target cell. These are classical geometry and symbolic decisions.', skills: [['contracts', 'Input/action contracts'], ['shape-geometry', 'Shape reconstruction'], ['symbols', 'Symbolic logic']] },
      plan: { title: 'Find a reachable token-to-cell transfer', description: 'Use robot geometry and inverse kinematics to plan motion. Screen reachability and clearance, then compose a transfer using the side-grasp and bimanual-transfer helpers. Integration does not imply a handover happens on every move.', skills: [['kinematics', 'Robot kinematics'], ['clearance', 'Clearance and reachability'], ['handover', 'Side grasps and bimanual transfer']] },
      act: { title: 'Execute, check placement, then observe again', description: 'Waypoint execution produces joint and gripper commands. Visual feedback and grasp checks assess retention and placement; the task controller reads the board again before continuing. Input/action contracts also validate output commands.', skills: [['waypoints', 'Cartesian waypoint execution'], ['feedback', 'Visual feedback and grasp checks']] }
    };
    const nodes = [...example.querySelectorAll('[data-primitive-stage]')];
    const select = node => {
      const stage = stages[node.dataset.primitiveStage];
      nodes.forEach(other => {
        other.classList.toggle('selected', other === node);
        other.setAttribute('aria-pressed', String(other === node));
      });
      example.querySelector('[data-primitive-title]').textContent = stage.title;
      example.querySelector('[data-primitive-description]').textContent = stage.description;
      const links = stage.skills.map(([id, label]) => {
        const link = document.createElement('a');
        link.href = `${reference}#primitive-${id}`;
        link.textContent = `${label} ↗`;
        return link;
      });
      example.querySelector('[data-primitive-links]').replaceChildren(...links);
    };
    nodes.forEach(node => {
      node.addEventListener('click', () => select(node));
      node.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); select(node); }
        if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
          event.preventDefault();
          const next = nodes[(nodes.indexOf(node) + (event.key === 'ArrowRight' ? 1 : -1) + nodes.length) % nodes.length];
          next.focus(); select(next);
        }
      });
    });
  }

  const rsiFlow = document.querySelector('[data-rsi-flow]');
  if (rsiFlow) {
    const stages = Object.freeze({
      generate: Object.freeze({
        index: '01 / Generate',
        title: 'Translate the task into executable policy code',
        description: 'The coding agent receives the instruction and simulation interface, then produces a controller that can act in the environment. This begins policy development; it is not yet the frozen evaluation.',
        facts: ['Task instruction', 'Environment interface', 'Controller code'],
      }),
      iterate: Object.freeze({
        index: '02 / Iterate',
        title: 'Run, inspect, and revise within the development budget',
        description: 'The controller runs in simulation while the agent reads success signals or diagnostics and revises the code. Feedback can change the policy only during this development loop.',
        facts: ['Simulation rollout', 'Success and diagnostics', 'Bounded revisions'],
      }),
      freeze: Object.freeze({
        index: '03 / Freeze',
        title: 'Select one artifact and end coding-agent intervention',
        description: 'One policy artifact is selected when development stops or the budget is exhausted. The artifact is locked before final evaluation, so later rollouts cannot trigger another code revision.',
        facts: ['Selected policy', 'No further edits', 'Locked evaluation input'],
      }),
      evaluate: Object.freeze({
        index: '04 / Evaluate',
        title: 'Run both evaluators on the same frozen rollout',
        description: 'The frozen controller executes on new evaluation seeds without coding-agent intervention. Origin-SR and Semantic-SR then read the same rollout, preserving a paired comparison.',
        facts: ['New evaluation seeds', 'Origin-SR', 'Semantic-SR'],
      }),
    });
    const nodes = [...rsiFlow.querySelectorAll('[data-rsi-stage]')];
    const selectStage = node => {
      const stage = stages[node.dataset.rsiStage];
      nodes.forEach(other => {
        const selected = other === node;
        other.classList.toggle('selected', selected);
        other.setAttribute('aria-pressed', String(selected));
      });
      rsiFlow.querySelector('[data-rsi-index]').textContent = stage.index;
      rsiFlow.querySelector('[data-rsi-title]').textContent = stage.title;
      rsiFlow.querySelector('[data-rsi-description]').textContent = stage.description;
      const facts = stage.facts.map(label => {
        const fact = document.createElement('span');
        fact.textContent = label;
        return fact;
      });
      rsiFlow.querySelector('[data-rsi-facts]').replaceChildren(...facts);
    };
    nodes.forEach(node => {
      node.addEventListener('click', () => selectStage(node));
      node.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          selectStage(node);
        }
        if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
          event.preventDefault();
          const step = event.key === 'ArrowRight' ? 1 : -1;
          const next = nodes[(nodes.indexOf(node) + step + nodes.length) % nodes.length];
          next.focus();
          selectStage(next);
        }
        if (event.key === 'Home' || event.key === 'End') {
          event.preventDefault();
          const next = event.key === 'Home' ? nodes[0] : nodes.at(-1);
          next.focus();
          selectStage(next);
        }
      });
    });
  }

  const resultsDashboard = document.querySelector('[data-results-dashboard]');
  const resultsTable = document.querySelector('[data-results-table]');
  if (resultsDashboard && resultsTable) {
    const table = resultsTable;
    const details = document.querySelector('[data-results-table-detail]');
    const chart = resultsDashboard.querySelector('[data-results-chart]');
    const search = resultsDashboard.querySelector('[data-results-search]');
    const sort = resultsDashboard.querySelector('[data-results-sort]');
    const status = resultsDashboard.querySelector('[data-results-status]');
    const empty = resultsDashboard.querySelector('[data-results-empty]');
    const filterButtons = [...resultsDashboard.querySelectorAll('[data-results-filter]')];
    const parseCount = cell => Number.parseInt(cell.textContent.replace(/[^0-9-]/g, ''), 10);
    const parseSummaryCount = cell => Number.parseInt(cell.textContent.split('/')[0].replace(/,/g, '').trim(), 10);
    const tasks = [...table.querySelectorAll('[data-task-row]')].map(row => {
      const cells = row.querySelectorAll('td');
      const origin = parseCount(cells[1]);
      const semantic = parseCount(cells[2]);
      return Object.freeze({
        name: cells[0].textContent.trim(),
        origin,
        semantic,
        both: parseCount(cells[3]),
        delta: semantic - origin,
        row,
      });
    });
    const summaryCells = table.querySelector('.summary-row').querySelectorAll('td');
    const statedTotals = summaryCells.length >= 3
      ? [parseSummaryCount(summaryCells[0]), parseSummaryCount(summaryCells[1]), parseSummaryCount(summaryCells[2])]
      : [];
    const rowTotals = tasks.reduce(
      (totals, task) => totals.map((value, index) => value + [task.origin, task.semantic, task.both][index]),
      [0, 0, 0],
    );
    const [origin, semantic, both] = rowTotals;
    if (statedTotals.length === 3 && rowTotals.some((value, index) => value !== statedTotals[index])) {
      console.warn('RoboTwin result summary does not match the task rows; the dashboard uses row-derived totals.');
    }
    const denominatorMatch = summaryCells[0].textContent.match(/\/\s*([\d,]+)/);
    const denominator = Number.parseInt(denominatorMatch[1].replace(/,/g, ''), 10);
    const taskDenominator = denominator / tasks.length;
    const outcomes = Object.freeze({
      both,
      'semantic-only': Math.max(0, semantic - both),
      'origin-only': Math.max(0, origin - both),
      neither: Math.max(0, denominator - origin - semantic + both),
    });
    let activeFilter = 'all';

    resultsDashboard.querySelector('[data-summary-value="origin"]').textContent = origin;
    resultsDashboard.querySelector('[data-summary-value="semantic"]').textContent = semantic;
    resultsDashboard.querySelector('[data-summary-value="both"]').textContent = both;
    resultsDashboard.querySelector('[data-outcome-total]').textContent = `${denominator.toLocaleString()} paired evaluations`;
    Object.entries(outcomes).forEach(([key, value]) => {
      resultsDashboard.querySelector(`[data-outcome-value="${key}"]`).textContent = value;
      const segment = resultsDashboard.querySelector(`[data-outcome-segment="${key}"]`);
      segment.style.width = `${value / denominator * 100}%`;
      segment.title = `${key.replace('-', ' ')}: ${value}`;
    });
    resultsDashboard.querySelector('[data-outcome-track]').setAttribute(
      'aria-label',
      `Of ${denominator} rollouts: ${both} succeeded under both evaluators, ${outcomes['semantic-only']} under Semantic only, ${outcomes['origin-only']} under Origin only, and ${outcomes.neither} under neither.`,
    );

    const createBar = (label, value, className) => {
      const line = document.createElement('span');
      line.className = 'dashboard-bar-line';
      const metric = document.createElement('span');
      metric.className = 'dashboard-bar-metric';
      metric.textContent = label;
      const track = document.createElement('span');
      track.className = 'dashboard-bar-track';
      const fill = document.createElement('span');
      fill.className = `dashboard-bar-fill ${className}`;
      fill.style.width = `${value / taskDenominator * 100}%`;
      const count = document.createElement('strong');
      count.textContent = value;
      track.append(fill);
      line.append(metric, track, count);
      return line;
    };

    const revealTask = task => {
      details.open = true;
      table.querySelectorAll('.dashboard-row-focus').forEach(row => row.classList.remove('dashboard-row-focus'));
      task.row.classList.add('dashboard-row-focus');
      task.row.tabIndex = -1;
      task.row.scrollIntoView({
        behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
        block: 'center',
      });
      task.row.focus({ preventScroll: true });
      status.textContent = `Opened ${task.name} in the complete result table.`;
    };

    const createTask = task => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'dashboard-task';
      button.setAttribute('aria-label', `${task.name}: Origin ${task.origin}, Semantic ${task.semantic}, both ${task.both}. Open this row in the complete table.`);
      const heading = document.createElement('span');
      heading.className = 'dashboard-task-heading';
      const name = document.createElement('code');
      name.textContent = task.name;
      const delta = document.createElement('span');
      delta.className = `dashboard-delta ${task.delta > 0 ? 'positive' : task.delta < 0 ? 'negative' : 'neutral'}`;
      delta.textContent = `${task.delta > 0 ? '+' : ''}${task.delta}`;
      heading.append(name, delta);
      const bars = document.createElement('span');
      bars.className = 'dashboard-task-bars';
      bars.append(createBar('O', task.origin, 'origin'), createBar('S', task.semantic, 'semantic'));
      const overlap = document.createElement('span');
      overlap.className = 'dashboard-overlap';
      overlap.textContent = `Both ${task.both} / ${taskDenominator} · open table row ↘`;
      button.append(heading, bars, overlap);
      button.addEventListener('click', () => revealTask(task));
      return button;
    };

    const matchesFilter = task => ({
      all: true,
      semantic: task.delta > 0,
      origin: task.delta < 0,
      equal: task.delta === 0,
      none: task.origin === 0 && task.semantic === 0,
    })[activeFilter];

    const comparators = {
      gap: (a, b) => Math.abs(b.delta) - Math.abs(a.delta) || b.semantic + b.origin - a.semantic - a.origin || a.name.localeCompare(b.name),
      semantic: (a, b) => b.semantic - a.semantic || b.origin - a.origin || a.name.localeCompare(b.name),
      origin: (a, b) => b.origin - a.origin || b.semantic - a.semantic || a.name.localeCompare(b.name),
      task: (a, b) => a.name.localeCompare(b.name),
    };

    const renderResults = () => {
      const words = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      const visible = tasks
        .filter(task => matchesFilter(task) && words.every(word => task.name.toLowerCase().includes(word)))
        .sort(comparators[sort.value]);
      chart.replaceChildren(...visible.map(createTask));
      empty.hidden = visible.length !== 0;
      chart.hidden = visible.length === 0;
      status.textContent = `${visible.length} of ${tasks.length} tasks · each bar shows successes out of ${taskDenominator}`;
      filterButtons.forEach(button => {
        const selected = button.dataset.resultsFilter === activeFilter;
        button.classList.toggle('active', selected);
        button.setAttribute('aria-pressed', String(selected));
      });
    };

    filterButtons.forEach(button => button.addEventListener('click', () => {
      activeFilter = button.dataset.resultsFilter;
      renderResults();
    }));
    search.addEventListener('input', renderResults);
    sort.addEventListener('change', renderResults);
    renderResults();
    resultsDashboard.hidden = false;
  }

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      const field = document.createElement('textarea');
      field.value = text; field.style.position = 'fixed'; field.style.opacity = '0';
      document.body.appendChild(field); field.select();
      const copied = document.execCommand('copy'); field.remove();
      if (!copied) throw new Error('Clipboard unavailable');
    }
  }

  document.querySelectorAll('[data-copy-citation]').forEach(button => {
    button.addEventListener('click', async () => {
      const block = button.closest('[data-citation]');
      const status = block.querySelector('[data-citation-status]');
      try {
        await copyText(block.querySelector('[data-citation-text]').textContent);
        button.textContent = 'Copied ✓';
        status.textContent = 'BibTeX citation copied.';
      } catch {
        status.textContent = 'Select and copy the citation above.';
      }
    });
  });

  const copy = document.querySelector('[data-copy]');
  if (copy) copy.addEventListener('click', async () => {
    const status = document.querySelector('[data-copy-status]');
    const url = location.href.split('#')[0];
    try {
      await copyText(url);
      copy.textContent = 'Link copied ✓'; status.textContent = 'Article link copied to clipboard.';
    } catch {
      copy.textContent = 'Copy the address above'; status.textContent = 'Clipboard unavailable. Copy this page’s address from your browser.';
    }
  });

  const tocLinks = [...document.querySelectorAll('.toc a')];
  if (tocLinks.length) {
    const sections = tocLinks.map(link => document.getElementById(link.hash.slice(1))).filter(Boolean);
    const updateToc = () => {
      let active = sections[0];
      sections.forEach(section => { if (section.getBoundingClientRect().top <= 160) active = section; });
      tocLinks.forEach(link => {
        const selected = link.hash === `#${active.id}`;
        link.classList.toggle('active', selected);
        if (selected) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    };
    window.addEventListener('scroll', updateToc, { passive: true }); updateToc();
  }

  // The preview endpoint exists only on serve.py. Static exports stop polling after a 404.
  let version;
  let disconnected = false;
  const liveReload = async () => {
    try {
      const response = await fetch('/__version', { cache: 'no-store' });
      if (!response.ok || !response.headers.get('content-type')?.includes('application/json')) return;
      const state = await response.json();
      if (version !== undefined && (version !== state.version || disconnected) && !state.error) { location.reload(); return; }
      version = state.version; disconnected = false;
      let error = document.querySelector('.dev-error');
      if (state.error) {
        if (!error) { error = document.createElement('div'); error.className = 'dev-error'; error.setAttribute('role', 'alert'); document.body.appendChild(error); }
        error.textContent = `Local build error — check your terminal and source files.\n${state.error}`;
      } else if (error) error.remove();
    } catch { disconnected = true; }
    setTimeout(liveReload, 1200);
  };
  if (['localhost', '127.0.0.1', '[::1]'].includes(location.hostname)) liveReload();
})();
