using System.Diagnostics;
using System.Globalization;

namespace ArbitraDocs.WinUI.Services;

public sealed record DocumentProcessOptions(
    bool NormalizeA4,
    bool PreserveExistingA4,
    double PageMarginMm,
    bool EnlargeSmallPages,
    bool Foliate,
    int StartNumber,
    string Direction,
    string Mode,
    string Position,
    string FontFamily,
    bool Bold,
    bool Italic,
    double FontSize,
    double FolioMarginXmm,
    double FolioMarginYmm,
    bool Certify,
    string? CertificatePdf);

public sealed class EngineService
{
    public async Task ProcessAsync(
        IReadOnlyList<string> inputPdfs,
        string outputPdf,
        DocumentProcessOptions options,
        CancellationToken cancellationToken = default)
    {
        if (inputPdfs.Count == 0)
        {
            throw new ArgumentException("No hay PDFs para procesar.", nameof(inputPdfs));
        }

        if (options.Certify && (string.IsNullOrWhiteSpace(options.CertificatePdf) || !File.Exists(options.CertificatePdf)))
        {
            throw new ArgumentException("Selecciona un PDF de certificación válido.", nameof(options));
        }

        var enginePath = FindEngine();
        var tempRoot = Directory.CreateTempSubdirectory("ArbitraDocs_");

        try
        {
            var merged = Path.Combine(tempRoot.FullName, "01_merged.pdf");
            var mergeArgs = new List<string> { "merge", merged };
            mergeArgs.AddRange(inputPdfs);
            await RunEngineAsync(enginePath, mergeArgs, cancellationToken);

            var current = merged;

            if (options.NormalizeA4)
            {
                var normalized = Path.Combine(tempRoot.FullName, "02_a4.pdf");
                var args = new List<string>
                {
                    "normalize",
                    current,
                    normalized,
                    "--margin-mm",
                    Invariant(options.PageMarginMm),
                };

                if (!options.PreserveExistingA4)
                {
                    args.Add("--no-preserve-a4");
                }

                if (options.EnlargeSmallPages)
                {
                    args.Add("--enlarge-small");
                }

                await RunEngineAsync(enginePath, args, cancellationToken);
                current = normalized;
            }

            if (options.Foliate)
            {
                var folioOutput = options.Certify
                    ? Path.Combine(tempRoot.FullName, "03_folio.pdf")
                    : outputPdf;

                var args = new List<string>
                {
                    "foliate",
                    current,
                    folioOutput,
                    "--start",
                    options.StartNumber.ToString(CultureInfo.InvariantCulture),
                    "--direction",
                    options.Direction,
                    "--mode",
                    options.Mode,
                    "--position",
                    options.Position,
                    "--font-family",
                    options.FontFamily,
                    "--font-size",
                    Invariant(options.FontSize),
                    "--margin-x-mm",
                    Invariant(options.FolioMarginXmm),
                    "--margin-y-mm",
                    Invariant(options.FolioMarginYmm),
                };

                if (options.Bold)
                {
                    args.Add("--bold");
                }

                if (options.Italic)
                {
                    args.Add("--italic");
                }

                await RunEngineAsync(enginePath, args, cancellationToken);
                current = folioOutput;
            }

            if (options.Certify)
            {
                await RunEngineAsync(
                    enginePath,
                    new[] { "certify", current, options.CertificatePdf!, outputPdf },
                    cancellationToken);
            }
            else if (!options.Foliate)
            {
                File.Copy(current, outputPdf, overwrite: true);
            }
        }
        finally
        {
            try
            {
                tempRoot.Delete(recursive: true);
            }
            catch
            {
                // Un temporal bloqueado no debe invalidar un PDF ya generado.
            }
        }
    }

    private static string FindEngine()
    {
        var configured = Environment.GetEnvironmentVariable("ARBITRADOCS_ENGINE_PATH");
        if (!string.IsNullOrWhiteSpace(configured) && File.Exists(configured))
        {
            return configured;
        }

        var candidates = new[]
        {
            Path.Combine(AppContext.BaseDirectory, "Engine", "ArbitraDocs.Engine.exe"),
            Path.Combine(AppContext.BaseDirectory, "ArbitraDocs.Engine.exe"),
        };

        foreach (var candidate in candidates)
        {
            if (File.Exists(candidate))
            {
                return candidate;
            }
        }

        throw new FileNotFoundException(
            "No se encontró el motor documental de ArbitraDocs. Reinstala la aplicación o usa el paquete completo de la beta.");
    }

    private static async Task RunEngineAsync(
        string enginePath,
        IEnumerable<string> arguments,
        CancellationToken cancellationToken)
    {
        var startInfo = new ProcessStartInfo(enginePath)
        {
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true,
        };

        foreach (var argument in arguments)
        {
            startInfo.ArgumentList.Add(argument);
        }

        using var process = Process.Start(startInfo)
            ?? throw new InvalidOperationException("No se pudo iniciar el motor documental.");

        var stdoutTask = process.StandardOutput.ReadToEndAsync(cancellationToken);
        var stderrTask = process.StandardError.ReadToEndAsync(cancellationToken);

        await process.WaitForExitAsync(cancellationToken);
        var stdout = await stdoutTask;
        var stderr = await stderrTask;

        if (process.ExitCode != 0)
        {
            var detail = string.IsNullOrWhiteSpace(stderr) ? stdout : stderr;
            throw new InvalidOperationException(
                string.IsNullOrWhiteSpace(detail)
                    ? $"El motor terminó con código {process.ExitCode}."
                    : detail.Trim());
        }
    }

    private static string Invariant(double value)
        => value.ToString("0.###", CultureInfo.InvariantCulture);
}
