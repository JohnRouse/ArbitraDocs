namespace ArbitraDocs.WinUI.Models;

public sealed class ExpedientAnalysisResult
{
    public string Source { get; set; } = string.Empty;
    public string OutputDirectory { get; set; } = string.Empty;
    public int DocumentsAnalyzed { get; set; }
    public int PagesAnalyzed { get; set; }
    public int OcrPages { get; set; }
    public List<ContractDetection> Contracts { get; set; } = new();
    public List<PaymentDetection> Payments { get; set; } = new();
    public List<string> Warnings { get; set; } = new();
}

public sealed class ContractDetection
{
    public string Title { get; set; } = string.Empty;
    public string? IssueDate { get; set; }
    public string SourcePath { get; set; } = string.Empty;
    public int StartPage { get; set; }
    public int EndPage { get; set; }
    public List<int> ArbitrationClausePages { get; set; } = new();
    public double Confidence { get; set; }
    public string OutputPdf { get; set; } = string.Empty;
    public string? ClausePdf { get; set; }

    public string PagesText => StartPage == EndPage ? StartPage.ToString() : $"{StartPage}-{EndPage}";
    public string ClausePagesText => ArbitrationClausePages.Count == 0
        ? "No detectada"
        : string.Join(", ", ArbitrationClausePages);
    public string ConfidenceText => $"{Confidence:P0}";
    public string IssueDateText => string.IsNullOrWhiteSpace(IssueDate) ? "No detectada" : IssueDate;
}

public sealed class PaymentDetection
{
    public string Description { get; set; } = string.Empty;
    public string? Date { get; set; }
    public string? Amount { get; set; }
    public string? Operation { get; set; }
    public string SourcePath { get; set; } = string.Empty;
    public int Page { get; set; }
    public double Confidence { get; set; }
    public string OutputPdf { get; set; } = string.Empty;

    public string DateText => string.IsNullOrWhiteSpace(Date) ? "No detectada" : Date;
    public string AmountText => string.IsNullOrWhiteSpace(Amount) ? "No detectado" : Amount;
    public string OperationText => string.IsNullOrWhiteSpace(Operation) ? "No detectada" : Operation;
    public string ConfidenceText => $"{Confidence:P0}";
}
