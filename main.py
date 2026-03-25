import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Task:
    title: str
    course: str
    task_type: str
    due: datetime
    est_hours: float
    priority: int
    movable: bool


class PlannerApp:
    DATE_FMT = "%Y-%m-%d %H:%M"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Intelligent Academic Planner")
        self.root.geometry("1100x700")

        self.tasks: list[Task] = []

        self._build_form()
        self._build_table()
        self._build_analysis()
        self.add_demo_tasks()

    def _build_form(self) -> None:
        frame = tk.LabelFrame(self.root, text="Add Task", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=8)

        self.title_var = tk.StringVar()
        self.course_var = tk.StringVar()
        self.type_var = tk.StringVar(value="assignment")
        self.due_var = tk.StringVar(value=datetime.now().strftime(self.DATE_FMT))
        self.hours_var = tk.StringVar(value="2")
        self.priority_var = tk.StringVar(value="3")
        self.movable_var = tk.BooleanVar(value=True)

        tk.Label(frame, text="Title").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.title_var, width=20).grid(row=1, column=0, padx=5)

        tk.Label(frame, text="Course").grid(row=0, column=1, sticky="w")
        tk.Entry(frame, textvariable=self.course_var, width=15).grid(row=1, column=1, padx=5)

        tk.Label(frame, text="Type").grid(row=0, column=2, sticky="w")
        ttk.Combobox(
            frame,
            textvariable=self.type_var,
            values=["assignment", "quiz", "exam", "project"],
            width=12,
            state="readonly",
        ).grid(row=1, column=2, padx=5)

        tk.Label(frame, text=f"Due ({self.DATE_FMT})").grid(row=0, column=3, sticky="w")
        tk.Entry(frame, textvariable=self.due_var, width=18).grid(row=1, column=3, padx=5)

        tk.Label(frame, text="Est. Hours").grid(row=0, column=4, sticky="w")
        tk.Entry(frame, textvariable=self.hours_var, width=10).grid(row=1, column=4, padx=5)

        tk.Label(frame, text="Priority (1-5)").grid(row=0, column=5, sticky="w")
        ttk.Combobox(
            frame,
            textvariable=self.priority_var,
            values=["1", "2", "3", "4", "5"],
            width=10,
            state="readonly",
        ).grid(row=1, column=5, padx=5)

        tk.Checkbutton(frame, text="Movable", variable=self.movable_var).grid(
            row=1, column=6, padx=8
        )

        tk.Button(frame, text="Add Task", command=self.add_task).grid(row=1, column=7, padx=5)
        tk.Button(frame, text="Delete Selected", command=self.delete_selected).grid(
            row=1, column=8, padx=5
        )
        tk.Button(frame, text="Analyze", command=self.refresh_analysis).grid(row=1, column=9, padx=5)

    def _build_table(self) -> None:
        frame = tk.LabelFrame(self.root, text="Tasks", padx=10, pady=10)
        frame.pack(fill="both", expand=True, padx=10, pady=8)

        cols = ("Title", "Course", "Type", "Due", "Hours", "Priority", "Movable")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c)

        self.tree.column("Title", width=180)
        self.tree.column("Course", width=100)
        self.tree.column("Type", width=90)
        self.tree.column("Due", width=150)
        self.tree.column("Hours", width=70, anchor="center")
        self.tree.column("Priority", width=70, anchor="center")
        self.tree.column("Movable", width=80, anchor="center")

        self.tree.pack(fill="both", expand=True)

    def _build_analysis(self) -> None:
        frame = tk.LabelFrame(self.root, text="Planner Insights", padx=10, pady=10)
        frame.pack(fill="both", expand=True, padx=10, pady=8)

        self.meter_label = tk.Label(frame, text="Workload Intensity: N/A", font=("Segoe UI", 11, "bold"))
        self.meter_label.pack(anchor="w")

        self.output = tk.Text(frame, height=12, wrap="word")
        self.output.pack(fill="both", expand=True, pady=8)

    def parse_datetime(self, value: str) -> datetime:
        return datetime.strptime(value, self.DATE_FMT)

    def add_task(self) -> None:
        try:
            task = Task(
                title=self.title_var.get().strip(),
                course=self.course_var.get().strip(),
                task_type=self.type_var.get().strip(),
                due=self.parse_datetime(self.due_var.get().strip()),
                est_hours=float(self.hours_var.get().strip()),
                priority=int(self.priority_var.get().strip()),
                movable=self.movable_var.get(),
            )
            if not task.title:
                raise ValueError("Title is required.")
            if task.priority < 1 or task.priority > 5:
                raise ValueError("Priority must be between 1 and 5.")
            if task.est_hours <= 0:
                raise ValueError("Estimated hours must be positive.")
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        self.tasks.append(task)
        self._insert_row(task)
        self.refresh_analysis()

    def _insert_row(self, task: Task) -> None:
        self.tree.insert(
            "",
            "end",
            values=(
                task.title,
                task.course,
                task.task_type,
                task.due.strftime(self.DATE_FMT),
                f"{task.est_hours:.1f}",
                task.priority,
                "Yes" if task.movable else "No",
            ),
        )

    def delete_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return

        # Delete from end so list indexes remain stable.
        indexes = [self.tree.index(item) for item in selected]
        for item in selected:
            self.tree.delete(item)

        for idx in sorted(indexes, reverse=True):
            if 0 <= idx < len(self.tasks):
                self.tasks.pop(idx)

        self.refresh_analysis()

    def detect_collisions(self, window_hours: int = 36) -> list[str]:
        collisions: list[str] = []
        ordered = sorted(self.tasks, key=lambda x: x.due)
        for i in range(len(ordered)):
            for j in range(i + 1, len(ordered)):
                gap = (ordered[j].due - ordered[i].due).total_seconds() / 3600
                if gap <= window_hours:
                    collisions.append(
                        f"- {ordered[i].title} ({ordered[i].due:%Y-%m-%d %H:%M}) and "
                        f"{ordered[j].title} ({ordered[j].due:%Y-%m-%d %H:%M}) gap={gap:.1f}h"
                    )
                else:
                    break
        return collisions

    def urgency_weight(self, due: datetime, now: datetime) -> float:
        days_left = (due - now).total_seconds() / 86400
        if days_left < 0:
            return 2.0
        if days_left <= 1:
            return 1.8
        if days_left <= 3:
            return 1.4
        if days_left <= 7:
            return 1.1
        return 0.9

    def task_score(self, task: Task, now: datetime) -> float:
        priority_weight = 0.8 + (task.priority * 0.2)
        return task.est_hours * priority_weight * self.urgency_weight(task.due, now)

    def workload_meter(self, now: datetime) -> tuple[float, str]:
        end = now + timedelta(days=7)
        upcoming = [t for t in self.tasks if now <= t.due <= end]
        score = sum(self.task_score(t, now) for t in upcoming)

        if score < 20:
            return score, "LOW"
        if score < 40:
            return score, "MEDIUM"
        return score, "HIGH"

    def weekly_forecast(self, now: datetime) -> list[str]:
        lines: list[str] = []
        for i in range(7):
            day = (now + timedelta(days=i)).date()
            day_tasks = [t for t in self.tasks if t.due.date() == day]
            score = sum(self.task_score(t, now) for t in day_tasks)
            if score < 5:
                lvl = "Low"
            elif score < 12:
                lvl = "Medium"
            else:
                lvl = "High"
            lines.append(f"- {day}: {lvl} (score={score:.2f})")
        return lines

    def redistribution(self, now: datetime) -> list[str]:
        suggestions: list[str] = []
        daily = {}
        for i in range(7):
            day = (now + timedelta(days=i)).date()
            day_tasks = [t for t in self.tasks if t.due.date() == day]
            score = sum(self.task_score(t, now) for t in day_tasks)
            daily[day] = score

        high_days = [d for d, s in daily.items() if s >= 12]
        for hd in high_days:
            movable = [
                t for t in self.tasks if t.due.date() == hd and t.movable and t.task_type.lower() != "exam"
            ]
            if not movable:
                suggestions.append(f"- {hd}: High load but no movable tasks.")
                continue
            low_before = [d for d, s in daily.items() if d < hd and s < 5]
            if low_before:
                target = low_before[-1]
                pick = max(movable, key=lambda t: t.est_hours)
                suggestions.append(f"- {hd}: Start '{pick.title}' earlier on {target} (1-2h prep).")
            else:
                suggestions.append(f"- {hd}: Begin tasks earlier this week to reduce pressure.")

        if not suggestions:
            suggestions.append("- No redistribution needed this week.")
        return suggestions

    def refresh_analysis(self) -> None:
        now = datetime.now()
        score, level = self.workload_meter(now)

        color = {"LOW": "green", "MEDIUM": "orange", "HIGH": "red"}.get(level, "black")
        self.meter_label.config(text=f"Workload Intensity: {level} (score={score:.2f})", fg=color)

        collisions = self.detect_collisions(window_hours=36)
        forecast = self.weekly_forecast(now)
        suggestions = self.redistribution(now)

        lines = []
        lines.append("1) Deadline Collision Detection")
        if collisions:
            lines.extend(collisions)
        else:
            lines.append("- No collisions within 36 hours.")

        lines.append("\n2) Weekly Stress Forecast")
        lines.extend(forecast)

        lines.append("\n3) Suggested Task Redistribution")
        lines.extend(suggestions)

        self.output.delete("1.0", "end")
        self.output.insert("1.0", "\n".join(lines))

    def add_demo_tasks(self) -> None:
        demo = [
            Task("Math Problem Set 5", "Math", "assignment", datetime.now() + timedelta(days=2), 5, 4, True),
            Task("CS Project Milestone", "CS", "project", datetime.now() + timedelta(days=3), 8, 5, True),
            Task("Physics Quiz", "Physics", "quiz", datetime.now() + timedelta(days=3, hours=6), 3, 4, True),
            Task("History Essay", "History", "assignment", datetime.now() + timedelta(days=5), 6, 3, True),
            Task("Chemistry Midterm", "Chem", "exam", datetime.now() + timedelta(days=6), 10, 5, False),
        ]
        for t in demo:
            self.tasks.append(t)
            self._insert_row(t)
        self.refresh_analysis()


if __name__ == "__main__":
    root = tk.Tk()
    app = PlannerApp(root)
    root.mainloop()
