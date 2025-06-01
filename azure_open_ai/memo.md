利用可能なモデルの一覧を表示する

```powershell
# 利用可能なSKUを表示
az cognitiveservices account list-skus --kind OpenAI --location japaneast

# モデルの一覧を表示
az cognitiveservices account list-models -n openai-service -g openai-rg

# 絞り込み
az cognitiveservices account list-models -n openai-service -g openai-rg --query "[?contains(name, 'gpt-4.1')]"
```