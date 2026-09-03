using ArbitraDocs.WinUI.Pages;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;

namespace ArbitraDocs.WinUI;

public sealed partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        Title = "ArbitraDocs";

        try
        {
            SystemBackdrop = new MicaBackdrop();
        }
        catch
        {
            // Windows 10 u otros entornos sin Mica usarán el fondo predeterminado.
        }

        NavigateHome();
    }

    public void NavigateToMergeFolio()
    {
        SelectNavigationItem("mergefolio");
        ContentFrame.Navigate(typeof(MergeFolioPage));
    }

    public void NavigateToInventory()
    {
        SelectNavigationItem("inventory");
        ContentFrame.Navigate(typeof(FileInventoryPage));
    }

    private void NavigateHome()
    {
        SelectNavigationItem("home");
        ContentFrame.Navigate(typeof(HomePage));
    }

    private void SelectNavigationItem(string tag)
    {
        foreach (var item in RootNavigation.MenuItems.OfType<NavigationViewItem>())
        {
            if (string.Equals(item.Tag?.ToString(), tag, StringComparison.OrdinalIgnoreCase))
            {
                RootNavigation.SelectedItem = item;
                break;
            }
        }
    }

    private void RootNavigation_SelectionChanged(
        NavigationView sender,
        NavigationViewSelectionChangedEventArgs args)
    {
        if (args.IsSettingsSelected)
        {
            ContentFrame.Navigate(typeof(SettingsPage));
            return;
        }

        var tag = args.SelectedItemContainer?.Tag?.ToString();
        switch (tag)
        {
            case "home":
                ContentFrame.Navigate(typeof(HomePage));
                break;
            case "mergefolio":
                ContentFrame.Navigate(typeof(MergeFolioPage));
                break;
            case "inventory":
                ContentFrame.Navigate(typeof(FileInventoryPage));
                break;
            case "pdf":
                ContentFrame.Navigate(typeof(CatalogPage), "pdf");
                break;
            case "convert":
                ContentFrame.Navigate(typeof(CatalogPage), "convert");
                break;
            case "special":
                ContentFrame.Navigate(typeof(CatalogPage), "special");
                break;
        }
    }
}
