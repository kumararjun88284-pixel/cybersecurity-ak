"""
FileSafe – File Integrity Checker
==================================
A Tkinter + hashlib desktop application for digital forensics demonstrations.
Run with:  python app.py

Features
--------
1. Single-file analysis  – compute the SHA-256 (and optionally MD5 / SHA-1)
                           digest of any file, together with its size and MIME
                           guess.
2. Hash comparison       – upload two files and detect whether they are byte-
                           for-byte identical by comparing their SHA-256 digests.
3. Known-hash verify     – paste a trusted hash and confirm whether the uploaded
                           file matches it (download verification workflow).
4. Hash history log      – every computed hash is appended to an in-session log
                           that can be saved to a .txt file for evidence records.
5. Educational panel     – embedded explanation of SHA-256, the avalanche effect,
                           and how hash verification is used in digital forensics.

Dependencies: tkinter (stdlib), hashlib (stdlib), os, mimetypes, datetime (all stdlib).
No pip-install required on Windows or macOS.
On Ubuntu/Debian Linux install Tkinter separately:
    sudo apt-get install python3-tk
"""

import hashlib
import mimetypes
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, font, messagebox, scrolledtext, ttk

# ── Colour palette ────────────────────────────────────────────────────────────
BG        = "#0d1117"
SURFACE   = "#161b22"
BORDER    = "#30363d"
TEXT      = "#e6edf3"
MUTED     = "#8b949e"
ACCENT    = "#58a6ff"
GREEN     = "#3fb950"
RED       = "#f85149"
GREEN_BG  = "#1a3a2a"
RED_BG    = "#3a1a1a"
MONO      = "Courier"

# ── Hash helpers ──────────────────────────────────────────────────────────────

def _read_file_bytes(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()

def compute_hashes(path: str) -> dict:
    """Return a dict with md5, sha1, sha256 hex digests plus size and mime."""
    data = _read_file_bytes(path)
    mime, _ = mimetypes.guess_type(path)
    return {
        "path"   : path,
        "name"   : os.path.basename(path),
        "size"   : len(data),
        "mime"   : mime or "application/octet-stream",
        "md5"    : hashlib.md5(data).hexdigest(),
        "sha1"   : hashlib.sha1(data).hexdigest(),
        "sha256" : hashlib.sha256(data).hexdigest(),
    }

def format_size(num: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} TB"

# ── Reusable widget helpers ───────────────────────────────────────────────────

def _label(parent, text, fg=TEXT, bg=BG, size=10, bold=False, mono=False):
    fam  = MONO if mono else "Segoe UI"
    wt   = "bold" if bold else "normal"
    return tk.Label(parent, text=text, fg=fg, bg=bg,
                    font=(fam, size, wt))

def _section_label(parent, text):
    """Blue section heading with a separator line underneath."""
    frame = tk.Frame(parent, bg=BG)
    frame.pack(fill="x", pady=(18, 6))
    tk.Label(frame, text=text, fg=ACCENT, bg=BG,
             font=("Segoe UI", 11, "bold")).pack(anchor="w")
    tk.Frame(frame, bg=BORDER, height=1).pack(fill="x", pady=(4, 0))

def _card_row(parent, label, value, mono_value=False):
    """Two-column label/value row inside a surface card."""
    row = tk.Frame(parent, bg=SURFACE)
    row.pack(fill="x", pady=2)
    tk.Label(row, text=label, fg=MUTED, bg=SURFACE,
             font=("Segoe UI", 8), width=14, anchor="w").pack(side="left", padx=(0, 8))
    fam = MONO if mono_value else "Segoe UI"
    tk.Label(row, text=value, fg=TEXT, bg=SURFACE,
             font=(fam, 9), anchor="w", wraplength=480, justify="left").pack(side="left")

def _card(parent):
    """A dark surface card frame."""
    f = tk.Frame(parent, bg=SURFACE, bd=0, relief="flat",
                 highlightbackground=BORDER, highlightthickness=1)
    f.pack(fill="x", pady=4, padx=2)
    inner = tk.Frame(f, bg=SURFACE)
    inner.pack(fill="x", padx=14, pady=10)
    return inner

def _result_banner(parent, match: bool):
    if match:
        msg, fg, bg = "✅  Hashes Match — the files are identical.", GREEN, GREEN_BG
    else:
        msg, fg, bg = "❌  Hashes Do Not Match — the files differ.", RED, RED_BG
    banner = tk.Frame(parent, bg=bg, highlightbackground=fg, highlightthickness=1)
    banner.pack(fill="x", pady=8, padx=2)
    tk.Label(banner, text=msg, fg=fg, bg=bg,
             font=("Segoe UI", 10, "bold")).pack(pady=10)

def _copy_btn(parent, text_to_copy):
    """Small 'Copy' button that writes text_to_copy to the clipboard."""
    def _copy():
        parent.clipboard_clear()
        parent.clipboard_append(text_to_copy)
    tk.Button(parent, text="Copy", fg=TEXT, bg=BORDER,
              activebackground=ACCENT, activeforeground=BG,
              bd=0, cursor="hand2", font=("Segoe UI", 8),
              command=_copy).pack(side="right", padx=4)

# ── Main application ──────────────────────────────────────────────────────────

class FileSafeApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FileSafe – File Integrity Checker")
        self.root.configure(bg=BG)
        self.root.geometry("760x680")
        self.root.resizable(True, True)
        self.root.minsize(600, 500)

        self.log_entries: list[str] = []  # session hash log

        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Title bar
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(18, 4))
        tk.Label(hdr, text="🔒 FileSafe", fg=TEXT, bg=BG,
                 font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Label(hdr, text="File Integrity Checker", fg=MUTED, bg=BG,
                 font=("Segoe UI", 10)).pack(side="left", padx=12, pady=4)

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(4, 0))

        # Notebook tabs
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",        background=BG,      borderwidth=0)
        style.configure("TNotebook.Tab",    background=SURFACE, foreground=MUTED,
                        padding=[14, 6],    font=("Segoe UI", 9))
        style.map("TNotebook.Tab",
                  background=[("selected", BG)],
                  foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=14, pady=10)

        self._tab_single   = self._scrollable_tab(nb, "🔍 Analyse File")
        self._tab_compare  = self._scrollable_tab(nb, "⚖️ Compare Files")
        self._tab_verify   = self._scrollable_tab(nb, "✔️ Verify Hash")
        self._tab_log      = self._scrollable_tab(nb, "📋 Hash Log")
        self._tab_about    = self._scrollable_tab(nb, "📚 About")

        self._build_single_tab()
        self._build_compare_tab()
        self._build_verify_tab()
        self._build_log_tab()
        self._build_about_tab()

    def _scrollable_tab(self, notebook, title: str):
        """Return an inner Frame inside a Canvas+Scrollbar tab."""
        outer = tk.Frame(notebook, bg=BG)
        notebook.add(outer, text=title)

        canvas    = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def _on_canvas_resize(event):
            canvas.itemconfig(win_id, width=event.width)

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_canvas_resize)

        # Mouse-wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        return inner  # callers pack widgets into this frame

    # ── Tab 1 – Single file analysis ─────────────────────────────────────────

    def _build_single_tab(self):
        p = self._tab_single
        pad = {"padx": 20}

        _section_label(p, "Single File Analysis")

        intro = tk.Label(p, bg=BG, fg=MUTED, font=("Segoe UI", 9),
                         text="Select any file to compute its SHA-256 (and MD5 / SHA-1) hash.",
                         anchor="w")
        intro.pack(fill="x", **pad)

        # File picker row
        pick_row = tk.Frame(p, bg=BG)
        pick_row.pack(fill="x", padx=20, pady=(10, 6))

        self._single_path_var = tk.StringVar()
        path_entry = tk.Entry(pick_row, textvariable=self._single_path_var,
                              bg=SURFACE, fg=TEXT, insertbackground=TEXT,
                              relief="flat", font=("Segoe UI", 9),
                              highlightbackground=BORDER, highlightthickness=1)
        path_entry.pack(side="left", fill="x", expand=True, ipady=5)

        tk.Button(pick_row, text="Browse…", fg=TEXT, bg=BORDER,
                  activebackground=ACCENT, activeforeground=BG,
                  bd=0, cursor="hand2", font=("Segoe UI", 9),
                  command=self._browse_single).pack(side="left", padx=(8, 0), ipady=5, ipadx=8)

        tk.Button(p, text="  Calculate Hashes  ", fg=TEXT,
                  bg="#238636", activebackground="#2ea043", activeforeground=TEXT,
                  bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"),
                  command=self._calc_single).pack(anchor="w", padx=20, pady=(0, 10), ipady=6)

        self._single_result_frame = tk.Frame(p, bg=BG)
        self._single_result_frame.pack(fill="x", padx=20)

    def _browse_single(self):
        path = filedialog.askopenfilename(title="Select a file")
        if path:
            self._single_path_var.set(path)

    def _calc_single(self):
        path = self._single_path_var.get().strip()
        if not path:
            messagebox.showwarning("No file", "Please select a file first.")
            return
        if not os.path.isfile(path):
            messagebox.showerror("File not found", f"Cannot read:\n{path}")
            return

        info = compute_hashes(path)
        self._render_single_result(info)
        self._append_log(info)

    def _render_single_result(self, info: dict):
        # Clear previous results
        for w in self._single_result_frame.winfo_children():
            w.destroy()

        card = _card(self._single_result_frame)
        _card_row(card, "File name",  info["name"])
        _card_row(card, "File size",  format_size(info["size"]))
        _card_row(card, "MIME type",  info["mime"])
        _card_row(card, "MD5",        info["md5"],    mono_value=True)
        _card_row(card, "SHA-1",      info["sha1"],   mono_value=True)
        _card_row(card, "SHA-256",    info["sha256"], mono_value=True)

        # Copy SHA-256 button
        btn_row = tk.Frame(self._single_result_frame, bg=BG)
        btn_row.pack(fill="x", pady=(0, 4))
        tk.Button(btn_row, text="Copy SHA-256", fg=TEXT, bg=BORDER,
                  activebackground=ACCENT, activeforeground=BG,
                  bd=0, cursor="hand2", font=("Segoe UI", 9),
                  command=lambda: [self.root.clipboard_clear(),
                                   self.root.clipboard_append(info["sha256"])]).pack(side="left")

    # ── Tab 2 – Compare two files ─────────────────────────────────────────────

    def _build_compare_tab(self):
        p = self._tab_compare
        pad = {"padx": 20}

        _section_label(p, "Compare Two Files")
        tk.Label(p, bg=BG, fg=MUTED, font=("Segoe UI", 9),
                 text="Select two files and compare their SHA-256 hashes to check for tampering.",
                 anchor="w").pack(fill="x", **pad)

        self._cmp_path_a = tk.StringVar()
        self._cmp_path_b = tk.StringVar()

        for label, var, cmd in [
            ("File 1:", self._cmp_path_a, lambda: self._browse_cmp("a")),
            ("File 2:", self._cmp_path_b, lambda: self._browse_cmp("b")),
        ]:
            row = tk.Frame(p, bg=BG)
            row.pack(fill="x", padx=20, pady=4)
            tk.Label(row, text=label, fg=TEXT, bg=BG,
                     font=("Segoe UI", 9), width=6, anchor="w").pack(side="left")
            tk.Entry(row, textvariable=var, bg=SURFACE, fg=TEXT,
                     insertbackground=TEXT, relief="flat", font=("Segoe UI", 9),
                     highlightbackground=BORDER, highlightthickness=1).pack(
                         side="left", fill="x", expand=True, ipady=5)
            tk.Button(row, text="Browse…", fg=TEXT, bg=BORDER,
                      activebackground=ACCENT, activeforeground=BG,
                      bd=0, cursor="hand2", font=("Segoe UI", 9),
                      command=cmd).pack(side="left", padx=(8, 0), ipady=5, ipadx=8)

        tk.Button(p, text="  Compare Hashes  ", fg=TEXT,
                  bg="#238636", activebackground="#2ea043", activeforeground=TEXT,
                  bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"),
                  command=self._do_compare).pack(anchor="w", padx=20, pady=(6, 10), ipady=6)

        self._cmp_result_frame = tk.Frame(p, bg=BG)
        self._cmp_result_frame.pack(fill="x", padx=20)

    def _browse_cmp(self, which: str):
        path = filedialog.askopenfilename(title=f"Select File {which.upper()}")
        if path:
            (self._cmp_path_a if which == "a" else self._cmp_path_b).set(path)

    def _do_compare(self):
        pa = self._cmp_path_a.get().strip()
        pb = self._cmp_path_b.get().strip()
        if not pa or not pb:
            messagebox.showwarning("Missing files", "Please select both files.")
            return
        for p in (pa, pb):
            if not os.path.isfile(p):
                messagebox.showerror("File not found", f"Cannot read:\n{p}")
                return

        info_a = compute_hashes(pa)
        info_b = compute_hashes(pb)

        # Clear previous results
        for w in self._cmp_result_frame.winfo_children():
            w.destroy()

        for label, info in [("File 1", info_a), ("File 2", info_b)]:
            tk.Label(self._cmp_result_frame, text=label, fg=ACCENT, bg=BG,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8, 2))
            card = _card(self._cmp_result_frame)
            _card_row(card, "File name", info["name"])
            _card_row(card, "File size", format_size(info["size"]))
            _card_row(card, "SHA-256",   info["sha256"], mono_value=True)

        _result_banner(self._cmp_result_frame, info_a["sha256"] == info_b["sha256"])

        self._append_log(info_a)
        self._append_log(info_b)

    # ── Tab 3 – Verify against known hash ────────────────────────────────────

    def _build_verify_tab(self):
        p = self._tab_verify
        pad = {"padx": 20}

        _section_label(p, "Verify Against Known Hash")
        tk.Label(p, bg=BG, fg=MUTED, font=("Segoe UI", 9),
                 text="Paste a trusted hash (e.g. from a download page) and confirm the file matches.",
                 anchor="w").pack(fill="x", **pad)

        # File picker
        file_row = tk.Frame(p, bg=BG)
        file_row.pack(fill="x", padx=20, pady=(10, 4))
        tk.Label(file_row, text="File:", fg=TEXT, bg=BG,
                 font=("Segoe UI", 9), width=6, anchor="w").pack(side="left")
        self._verify_path_var = tk.StringVar()
        tk.Entry(file_row, textvariable=self._verify_path_var, bg=SURFACE, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 9),
                 highlightbackground=BORDER, highlightthickness=1).pack(
                     side="left", fill="x", expand=True, ipady=5)
        tk.Button(file_row, text="Browse…", fg=TEXT, bg=BORDER,
                  activebackground=ACCENT, activeforeground=BG,
                  bd=0, cursor="hand2", font=("Segoe UI", 9),
                  command=self._browse_verify).pack(side="left", padx=(8, 0), ipady=5, ipadx=8)

        # Known-hash entry
        hash_row = tk.Frame(p, bg=BG)
        hash_row.pack(fill="x", padx=20, pady=4)
        tk.Label(hash_row, text="Known\nhash:", fg=TEXT, bg=BG,
                 font=("Segoe UI", 9), width=6, anchor="w").pack(side="left")
        self._known_hash_var = tk.StringVar()
        tk.Entry(hash_row, textvariable=self._known_hash_var, bg=SURFACE, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=(MONO, 9),
                 highlightbackground=BORDER, highlightthickness=1).pack(
                     side="left", fill="x", expand=True, ipady=5)

        # Algorithm radio buttons
        algo_row = tk.Frame(p, bg=BG)
        algo_row.pack(fill="x", padx=20, pady=4)
        tk.Label(algo_row, text="Algorithm:", fg=TEXT, bg=BG,
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 10))
        self._algo_var = tk.StringVar(value="sha256")
        for algo in ("md5", "sha1", "sha256"):
            tk.Radiobutton(algo_row, text=algo.upper(), variable=self._algo_var,
                           value=algo, fg=TEXT, bg=BG, selectcolor=SURFACE,
                           activebackground=BG, activeforeground=ACCENT,
                           font=("Segoe UI", 9)).pack(side="left", padx=6)

        tk.Button(p, text="  Verify  ", fg=TEXT,
                  bg="#238636", activebackground="#2ea043", activeforeground=TEXT,
                  bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"),
                  command=self._do_verify).pack(anchor="w", padx=20, pady=(6, 10), ipady=6)

        self._verify_result_frame = tk.Frame(p, bg=BG)
        self._verify_result_frame.pack(fill="x", padx=20)

    def _browse_verify(self):
        path = filedialog.askopenfilename(title="Select file to verify")
        if path:
            self._verify_path_var.set(path)

    def _do_verify(self):
        path       = self._verify_path_var.get().strip()
        known_hash = self._known_hash_var.get().strip().lower()
        algo       = self._algo_var.get()

        if not path:
            messagebox.showwarning("No file", "Please select a file.")
            return
        if not known_hash:
            messagebox.showwarning("No hash", "Please paste the known hash.")
            return
        if not os.path.isfile(path):
            messagebox.showerror("File not found", f"Cannot read:\n{path}")
            return

        info = compute_hashes(path)
        computed = info[algo]
        match    = computed == known_hash

        for w in self._verify_result_frame.winfo_children():
            w.destroy()

        card = _card(self._verify_result_frame)
        _card_row(card, "File",      info["name"])
        _card_row(card, "Algorithm", algo.upper())
        _card_row(card, "Known",     known_hash, mono_value=True)
        _card_row(card, "Computed",  computed,   mono_value=True)

        _result_banner(self._verify_result_frame, match)
        self._append_log(info)

    # ── Tab 4 – Hash log ──────────────────────────────────────────────────────

    def _build_log_tab(self):
        p = self._tab_log

        _section_label(p, "Hash History Log")
        tk.Label(p, bg=BG, fg=MUTED, font=("Segoe UI", 9),
                 text="Every hash computed this session is recorded here. Save to .txt for evidence records.",
                 anchor="w").pack(fill="x", padx=20)

        self._log_text = scrolledtext.ScrolledText(
            p, bg=SURFACE, fg=TEXT, insertbackground=TEXT,
            font=(MONO, 8), relief="flat",
            highlightbackground=BORDER, highlightthickness=1,
            state="disabled", height=18)
        self._log_text.pack(fill="both", expand=True, padx=20, pady=10)

        btn_row = tk.Frame(p, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=(0, 10))
        tk.Button(btn_row, text="Save Log…", fg=TEXT, bg=BORDER,
                  activebackground=ACCENT, activeforeground=BG,
                  bd=0, cursor="hand2", font=("Segoe UI", 9),
                  command=self._save_log).pack(side="left", ipady=5, ipadx=10)
        tk.Button(btn_row, text="Clear Log", fg=RED, bg=BORDER,
                  activebackground=RED_BG, activeforeground=RED,
                  bd=0, cursor="hand2", font=("Segoe UI", 9),
                  command=self._clear_log).pack(side="left", padx=8, ipady=5, ipadx=10)

    def _append_log(self, info: dict):
        ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = (
            f"[{ts}]\n"
            f"  File   : {info['path']}\n"
            f"  Size   : {format_size(info['size'])}\n"
            f"  MD5    : {info['md5']}\n"
            f"  SHA-1  : {info['sha1']}\n"
            f"  SHA-256: {info['sha256']}\n"
            f"{'-'*72}\n"
        )
        self.log_entries.append(entry)
        self._log_text.configure(state="normal")
        self._log_text.insert("end", entry)
        self._log_text.see("end")
        self._log_text.configure(state="disabled")

    def _save_log(self):
        if not self.log_entries:
            messagebox.showinfo("Empty log", "No hashes have been computed yet.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save hash log")
        if path:
            with open(path, "w", encoding="utf-8") as fh:
                fh.writelines(self.log_entries)
            messagebox.showinfo("Saved", f"Log saved to:\n{path}")

    def _clear_log(self):
        if messagebox.askyesno("Clear log", "Delete all log entries?"):
            self.log_entries.clear()
            self._log_text.configure(state="normal")
            self._log_text.delete("1.0", "end")
            self._log_text.configure(state="disabled")

    # ── Tab 5 – About / educational panel ────────────────────────────────────

    def _build_about_tab(self):
        p = self._tab_about

        _section_label(p, "What is File Integrity & Hashing?")

        sections = [
            ("File Integrity",
             "Ensuring a file has not been altered, corrupted, or tampered with "
             "since it was created or last verified. Even a single changed byte "
             "produces a completely different hash — this property is called the "
             "avalanche effect."),
            ("SHA-256 (Secure Hash Algorithm 256-bit)",
             "A one-way cryptographic function. It takes any input and produces a "
             "fixed-length 64-character hexadecimal digest. The same input always "
             "produces the same digest, but you cannot reverse the digest back to "
             "the original file."),
            ("Digital Forensics Use",
             "Investigators hash every piece of evidence the moment it is collected. "
             "If the hash computed later matches the original, the evidence is "
             "provably untouched — this is legally admissible in court because "
             "SHA-256 collisions are computationally infeasible with current hardware."),
            ("Common Use-Cases",
             "• Verifying downloaded software against the publisher's posted hash\n"
             "• Detecting malware by comparing a system file against a known-good DB\n"
             "• Preserving chain-of-custody for digital evidence\n"
             "• Ensuring backup integrity after transfer or storage"),
        ]

        for title, body in sections:
            frame = tk.Frame(p, bg=SURFACE,
                             highlightbackground=BORDER, highlightthickness=1)
            frame.pack(fill="x", padx=20, pady=5)
            inner = tk.Frame(frame, bg=SURFACE)
            inner.pack(fill="x", padx=14, pady=10)
            tk.Label(inner, text=title, fg=ACCENT, bg=SURFACE,
                     font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x")
            tk.Label(inner, text=body, fg=TEXT, bg=SURFACE,
                     font=("Segoe UI", 9), anchor="w", justify="left",
                     wraplength=660).pack(fill="x", pady=(4, 0))

        # Footer
        tk.Label(p, text="FileSafe · Built with Tkinter · All processing is local — no data leaves your machine.",
                 fg=MUTED, bg=BG, font=("Segoe UI", 8)).pack(pady=(20, 10))


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    app  = FileSafeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
