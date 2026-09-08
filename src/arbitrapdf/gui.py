from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from arbitrapdf.core.foliation import FolioOptions
from arbitrapdf.core.normalize import NormalizationOptions
from arbitrapdf.core.pipeline import merge_normalize_and_foliate


class ArbitraDocsApp(tk.Tk):
    """Primera interfaz de prueba de ArbitraDocs.

    Esta beta concentra el flujo que ya está validado en el motor:
    unir -> normalizar A4 opcional -> foliar opcional.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("ArbitraDocs — Beta 0.1")
        self.geometry("930x720")
        self.minsize(820, 650)
        self.files: list[Path] = []

        self._build_style()
        self._build_ui()

    def _build_style(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=8)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="ArbitraDocs", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            root,
            text="Beta de escritorio · Unir PDF + A4 + foliación",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 14))

        files_frame = ttk.LabelFrame(root, text="1. PDFs y orden", style="Section.TLabelframe")
        files_frame.pack(fill="both", expand=True)

        list_frame = ttk.Frame(files_frame, padding=10)
        list_frame.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, activestyle="none")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btns = ttk.Frame(files_frame, padding=(10, 0, 10, 10))
        btns.pack(fill="x")
        ttk.Button(btns, text="Agregar PDF", command=self.add_files).pack(side="left")
        ttk.Button(btns, text="Quitar", command=self.remove_selected).pack(side="left", padx=5)
        ttk.Button(btns, text="Subir", command=lambda: self.move_selected(-1)).pack(side="left", padx=(12, 5))
        ttk.Button(btns, text="Bajar", command=lambda: self.move_selected(1)).pack(side="left")
        ttk.Button(btns, text="Limpiar", command=self.clear_files).pack(side="right")

        options = ttk.Frame(root)
        options.pack(fill="x", pady=(14, 0))
        options.columnconfigure(0, weight=1)
        options.columnconfigure(1, weight=1)

        a4 = ttk.LabelFrame(options, text="2. Página / A4", style="Section.TLabelframe", padding=12)
        a4.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

        self.normalize_var = tk.BooleanVar(value=True)
        self.preserve_a4_var = tk.BooleanVar(value=True)
        self.enlarge_var = tk.BooleanVar(value=False)
        self.page_margin_var = tk.DoubleVar(value=8.0)

        ttk.Checkbutton(a4, text="Normalizar salida a A4 vertical", variable=self.normalize_var).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(
            a4,
            text="Conservar A4 existente al 100 %",
            variable=self.preserve_a4_var,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        ttk.Label(
            a4,
            text="Desmárcalo si deseas aplicar el margen también a páginas que ya son A4.",
            wraplength=350,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(1, 7))
        ttk.Label(a4, text="Margen de página (mm):").grid(row=3, column=0, sticky="w")
        ttk.Spinbox(a4, from_=0, to=40, increment=0.5, textvariable=self.page_margin_var, width=8).grid(row=3, column=1, sticky="w")
        ttk.Checkbutton(a4, text="Ampliar páginas pequeñas", variable=self.enlarge_var).grid(row=4, column=0, columnspan=2, sticky="w", pady=(7, 0))

        folio = ttk.LabelFrame(options, text="3. Foliación", style="Section.TLabelframe", padding=12)
        folio.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

        self.foliate_var = tk.BooleanVar(value=True)
        self.start_var = tk.IntVar(value=1)
        self.direction_var = tk.StringVar(value="Ascendente")
        self.mode_var = tk.StringVar(value="Número + letras")
        self.position_var = tk.StringVar(value="Superior derecha")
        self.font_size_var = tk.DoubleVar(value=8.0)
        self.folio_margin_x_var = tk.DoubleVar(value=10.0)
        self.folio_margin_y_var = tk.DoubleVar(value=6.0)

        ttk.Checkbutton(folio, text="Foliar PDF final", variable=self.foliate_var).grid(row=0, column=0, columnspan=2, sticky="w")
        self._row(folio, 1, "Número inicial:", ttk.Spinbox(folio, from_=0, to=9999999, textvariable=self.start_var, width=12))
        self._row(folio, 2, "Sentido:", ttk.Combobox(folio, textvariable=self.direction_var, values=["Ascendente", "Descendente"], state="readonly", width=20))
        self._row(folio, 3, "Formato:", ttk.Combobox(folio, textvariable=self.mode_var, values=["Número", "Letras", "Número + letras"], state="readonly", width=20))
        self._row(folio, 4, "Posición:", ttk.Combobox(folio, textvariable=self.position_var, values=["Superior derecha", "Superior centro", "Superior izquierda", "Inferior derecha", "Inferior centro", "Inferior izquierda"], state="readonly", width=20))
        self._row(folio, 5, "Tamaño de letra:", ttk.Spinbox(folio, from_=5.5, to=30, increment=0.5, textvariable=self.font_size_var, width=8))
        self._row(folio, 6, "Margen horizontal (mm):", ttk.Spinbox(folio, from_=0, to=50, increment=0.5, textvariable=self.folio_margin_x_var, width=8))
        self._row(folio, 7, "Margen vertical (mm):", ttk.Spinbox(folio, from_=0, to=50, increment=0.5, textvariable=self.folio_margin_y_var, width=8))

        bottom = ttk.Frame(root)
        bottom.pack(fill="x", pady=(14, 0))
        self.status_var = tk.StringVar(value="Listo.")
        ttk.Label(bottom, textvariable=self.status_var).pack(side="left")
        self.progress = ttk.Progressbar(bottom, mode="indeterminate", length=180)
        self.progress.pack(side="left", padx=12)
        self.process_btn = ttk.Button(bottom, text="Crear PDF", style="Primary.TButton", command=self.start_processing)
        self.process_btn.pack(side="right")

    @staticmethod
    def _row(parent: ttk.Frame, row: int, label: str, widget: tk.Widget) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3, padx=(0, 8))
        widget.grid(row=row, column=1, sticky="w", pady=3)

    def add_files(self) -> None:
        names = filedialog.askopenfilenames(title="Seleccionar PDFs", filetypes=[("PDF", "*.pdf")])
        for name in names:
            path = Path(name)
            self.files.append(path)
            self.listbox.insert(tk.END, path.name)

    def remove_selected(self) -> None:
        indexes = list(self.listbox.curselection())
        for idx in reversed(indexes):
            self.listbox.delete(idx)
            del self.files[idx]

    def clear_files(self) -> None:
        self.files.clear()
        self.listbox.delete(0, tk.END)

    def move_selected(self, direction: int) -> None:
        selected = list(self.listbox.curselection())
        if len(selected) != 1:
            if selected:
                messagebox.showinfo("Orden", "Selecciona un solo archivo para moverlo.")
            return
        idx = selected[0]
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(self.files):
            return
        self.files[idx], self.files[new_idx] = self.files[new_idx], self.files[idx]
        self._refresh_list(new_idx)

    def _refresh_list(self, select_index: int | None = None) -> None:
        self.listbox.delete(0, tk.END)
        for path in self.files:
            self.listbox.insert(tk.END, path.name)
        if select_index is not None:
            self.listbox.selection_set(select_index)
            self.listbox.activate(select_index)

    def _folio_options(self) -> FolioOptions | None:
        if not self.foliate_var.get():
            return None
        directions = {"Ascendente": "asc", "Descendente": "desc"}
        modes = {"Número": "numero", "Letras": "letras", "Número + letras": "numero+letras"}
        positions = {
            "Superior derecha": "top-right",
            "Superior centro": "top-center",
            "Superior izquierda": "top-left",
            "Inferior derecha": "bottom-right",
            "Inferior centro": "bottom-center",
            "Inferior izquierda": "bottom-left",
        }
        return FolioOptions(
            start=int(self.start_var.get()),
            direction=directions[self.direction_var.get()],
            mode=modes[self.mode_var.get()],
            position=positions[self.position_var.get()],
            font_size=float(self.font_size_var.get()),
            margin_x_mm=float(self.folio_margin_x_var.get()),
            margin_y_mm=float(self.folio_margin_y_var.get()),
        )

    def start_processing(self) -> None:
        if not self.files:
            messagebox.showwarning("ArbitraDocs", "Agrega al menos un PDF.")
            return
        output = filedialog.asksaveasfilename(
            title="Guardar PDF final",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile="ArbitraDocs_resultado.pdf",
        )
        if not output:
            return

        try:
            margin = float(self.page_margin_var.get())
            if not 0 <= margin <= 40:
                raise ValueError("El margen de página debe estar entre 0 y 40 mm.")
            norm = NormalizationOptions(
                margin_mm=margin,
                preserve_a4=bool(self.preserve_a4_var.get()),
                enlarge_small_pages=bool(self.enlarge_var.get()),
            )
            folio = self._folio_options()
        except Exception as exc:
            messagebox.showerror("Configuración", str(exc))
            return

        self.process_btn.configure(state="disabled")
        self.progress.start(10)
        self.status_var.set("Procesando…")

        worker = threading.Thread(
            target=self._process,
            args=(list(self.files), Path(output), norm, folio),
            daemon=True,
        )
        worker.start()

    def _process(self, inputs: list[Path], output: Path, norm: NormalizationOptions, folio: FolioOptions | None) -> None:
        try:
            merge_normalize_and_foliate(
                inputs,
                output,
                normalize=bool(self.normalize_var.get()),
                normalization_options=norm,
                folio_options=folio,
            )
        except Exception as exc:
            self.after(0, self._finished_error, str(exc))
            return
        self.after(0, self._finished_ok, output)

    def _finished_ok(self, output: Path) -> None:
        self.progress.stop()
        self.process_btn.configure(state="normal")
        self.status_var.set(f"Terminado: {output.name}")
        messagebox.showinfo("ArbitraDocs", f"PDF creado correctamente:\n\n{output}")

    def _finished_error(self, detail: str) -> None:
        self.progress.stop()
        self.process_btn.configure(state="normal")
        self.status_var.set("Error durante el procesamiento.")
        messagebox.showerror("ArbitraDocs", detail)


def main() -> None:
    app = ArbitraDocsApp()
    app.mainloop()


if __name__ == "__main__":
    main()
