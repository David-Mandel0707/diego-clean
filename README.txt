O código será rodado a partir do main branch, então apenas mudanças registradas lá serão rodadas. 
Para atualizar branch de acordo com a main, abar o terminal e use:
  git checkout SEU_BRANCH
  git merge main
  git push origin SEU_BRANCH
Para commitar as mudanças em seu próprio branch, abra o terminal e use:
  git add .
  git commit -m "NOME_DO_COMMIT"
  git push origin SEU_BRANCH
Para atualizar o main de acordo com sua branch, abra o terminal e use:
  git checkout main
  git merge SEU_BRANCH
  git push origin main