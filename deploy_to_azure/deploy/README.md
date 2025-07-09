実行サンプル

```powershell
.\deploy.ps1 -ResourceGroupName "HogeRG" -Location "japaneast" -AdminUsername "hogeadmin" -FrontendImage "docker.io/hogehoge/ragchat-frontend-blazor:0.0.1" -BackendImage "docker.io/hogehoge/ragchat-backend:0.0.1"
```