import getQuestion from "./questapi.js";

let perguntas = [];
let currentIndex = 0;
let acertos = 0;
let erros = 0;
let pontuacao = 0;
const limiteQuestoes = 4;
let resultado = [];

async function carregarPerguntas() {
  const todasPerguntas = await getQuestion();
  perguntas = selecionarPerguntasAleatorias(todasPerguntas, limiteQuestoes);
  mostrarPergunta();
}

function atualizarQuantidade() {
  document.getElementById("questao").innerText = `Questão: ${currentIndex + 1}/${limiteQuestoes}`;
  document.getElementById("acertos").innerText = `Acertos: ${acertos}`;
  document.getElementById("erros").innerText = `Erros: ${erros}`;
}

function selecionarPerguntasAleatorias(array, qtd) {
  return array.sort(() => Math.random() - 0.5).slice(0, qtd);
}

function mostrarPergunta() {
  if (currentIndex >= limiteQuestoes || currentIndex >= perguntas.length) {
    alert("Fim do quiz!");
    return;
  }
  const p = perguntas[currentIndex];
  document.getElementById("quest").innerHTML = p.pergunta;
  document.getElementById("a").innerHTML = p.respostas[0].texto;
  document.getElementById("b").innerHTML = p.respostas[1].texto;
  document.getElementById("c").innerHTML = p.respostas[2].texto;
  document.getElementById("d").innerHTML = p.respostas[3].texto;
  atualizarQuantidade();
}

async function enviarPontuacaoFinal(pontos) {
  try {
    //envia a pontuação 
    const resposta = await fetch('/salvar_pontuacao', {
      method: 'POST', 
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ pontos: pontos }) 
    });

    // verifica se teve erro no servidor
    if (!resposta.ok) { 
      const mensagemElemento = document.getElementById("mensagem-ranking");
      if (mensagemElemento) { 
        mensagemElemento.innerText = "Você precisa estar logado para participar do ranking.";
      }
      return; 
    }

    // se nao teve erro, carrega o ranking
    await carregarRanking();

  } catch (erro) {
    // mostra essa mensagem se der tudo errado
    console.error('Erro ao enviar pontuação:', erro);
  }
}
//carrega o ranking
async function carregarRanking() {
  try {
    const resposta = await fetch('/ranking'); 

    // mensagem de erro
    if (!resposta.ok) { 
      console.error('Erro ao buscar ranking: A requisição não foi bem-sucedida.');
      return; 
    }

    const ranking = await resposta.json();

 
    const rankingDiv = document.getElementById('ranking-container');

    // verifica se existe
    if (!rankingDiv) {
      console.error('Elemento "ranking-container" não encontrado na página.');
      return;
    }

    // html do ranking
    rankingDiv.innerHTML = '<h2>Ranking</h2>'; 

    // 7. Verificar se o ranking está vazio
    if (ranking.length === 0) {
      rankingDiv.innerHTML += '<p>Nenhuma pontuação ainda.</p>'; // Mostra mensagem de que nao tem pontuaçao
      return; 
    }

    // cria uma liste se tiver pontuaçao
    let listaHTML = '<ol>';
    ranking.forEach((item) => {
      // nome,posiçao e pontos
      listaHTML += `<li>${item.posicao}. ${item.nome} - ${item.pontos} pontos</li>`;
    });
    listaHTML += '</ol>'; 

    // coloca a lista do rankking no html
    rankingDiv.innerHTML += listaHTML;

  } catch (erro) {
    // erro se der tudo errado
    console.error('Erro ao carregar ranking:', erro);
  }
}

export function checarResposta(indice, event) {
  const correta = perguntas[currentIndex].respostas[indice].correta;

  if (correta) {
    acertos++;
    resultado.push(10);
    event.target.style.backgroundColor = "green";
  } else {
    erros++;
    event.target.style.backgroundColor = "red";
  }

  currentIndex++;

  setTimeout(() => {
    if (currentIndex < limiteQuestoes && currentIndex < perguntas.length) {
      mostrarPergunta();
      document.getElementById("a").style.backgroundColor = "";
      document.getElementById("b").style.backgroundColor = "";
      document.getElementById("c").style.backgroundColor = "";
      document.getElementById("d").style.backgroundColor = "";
    } else {
      pontuacao = resultado.reduce((acc, val) => acc + val, 0);

      document.getElementById("quiz-container").style.display = "none";
      document.getElementById("resultado-container").style.display = "block";

      // mostra os resultados na tela
      document.getElementById("acertos-final").innerText = `Acertos: ${acertos}`;
      document.getElementById("erros-final").innerText = `Erros: ${erros}`;
      document.getElementById("resultado-texto").innerText = `Sua pontuação final foi: ${pontuacao} pontos`;

      enviarPontuacaoFinal(pontuacao);

      // Reseta para novo jogo
      acertos = 0;
      erros = 0;
      currentIndex = 0;
      resultado = [];
      carregarPerguntas();
    }
  }, 1000);
}

window.onload = function () {
  document.getElementById("a").onclick = (e) => checarResposta(0, e);
  document.getElementById("b").onclick = (e) => checarResposta(1, e);
  document.getElementById("c").onclick = (e) => checarResposta(2, e);
  document.getElementById("d").onclick = (e) => checarResposta(3, e);
  carregarPerguntas();
};

window.reiniciarQuiz = function () {
  window.location.href = "/jogo";
};

window.sairQuiz = function () {
  window.location.href = "/";
};

window.verRanking = function () {
  window.location.href = "/ranking";
};
