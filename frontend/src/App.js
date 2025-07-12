import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [workers, setWorkers] = useState([]);
  const [selectedWorker, setSelectedWorker] = useState(null);
  const [showAddWorker, setShowAddWorker] = useState(false);
  const [showAddTransaction, setShowAddTransaction] = useState(false);
  const [loading, setLoading] = useState(true);

  // Form states
  const [newWorker, setNewWorker] = useState({
    name: "",
    position: "",
    phone: ""
  });
  
  const [newTransaction, setNewTransaction] = useState({
    worker_id: "",
    type: "due",
    amount: "",
    description: ""
  });

  // Fetch workers with balances
  const fetchWorkersBalances = async () => {
    try {
      const response = await axios.get(`${API}/workers-balances`);
      setWorkers(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Erreur lors du chargement des ouvriers:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkersBalances();
  }, []);

  // Add new worker
  const handleAddWorker = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/workers`, newWorker);
      setNewWorker({ name: "", position: "", phone: "" });
      setShowAddWorker(false);
      await fetchWorkersBalances();
    } catch (error) {
      console.error("Erreur lors de l'ajout de l'ouvrier:", error);
      alert("Erreur lors de l'ajout de l'ouvrier");
    }
  };

  // Add new transaction
  const handleAddTransaction = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/transactions`, {
        ...newTransaction,
        amount: parseFloat(newTransaction.amount)
      });
      setNewTransaction({ worker_id: "", type: "due", amount: "", description: "" });
      setShowAddTransaction(false);
      await fetchWorkersBalances();
    } catch (error) {
      console.error("Erreur lors de l'ajout de la transaction:", error);
      alert("Erreur lors de l'ajout de la transaction");
    }
  };

  // Delete worker
  const handleDeleteWorker = async (workerId) => {
    if (window.confirm("Êtes-vous sûr de vouloir supprimer cet ouvrier et toutes ses transactions ?")) {
      try {
        await axios.delete(`${API}/workers/${workerId}`);
        await fetchWorkersBalances();
      } catch (error) {
        console.error("Erreur lors de la suppression:", error);
        alert("Erreur lors de la suppression");
      }
    }
  };

  // Delete transaction
  const handleDeleteTransaction = async (transactionId) => {
    if (window.confirm("Êtes-vous sûr de vouloir supprimer cette transaction ?")) {
      try {
        await axios.delete(`${API}/transactions/${transactionId}`);
        await fetchWorkersBalances();
        // Refresh selected worker if viewing details
        if (selectedWorker) {
          const updatedWorker = workers.find(w => w.worker.id === selectedWorker.worker.id);
          setSelectedWorker(updatedWorker);
        }
      } catch (error) {
        console.error("Erreur lors de la suppression de la transaction:", error);
        alert("Erreur lors de la suppression de la transaction");
      }
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl text-gray-600">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            💰 Gestion des Paies Ouvriers
          </h1>
          <p className="text-gray-600">
            Gérez facilement les salaires dus et payés à vos ouvriers
          </p>
        </header>

        {/* Action buttons */}
        <div className="mb-6 flex gap-4">
          <button
            onClick={() => setShowAddWorker(true)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            ➕ Ajouter un ouvrier
          </button>
          <button
            onClick={() => setShowAddTransaction(true)}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            💸 Ajouter une transaction
          </button>
        </div>

        {/* Workers list */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {workers.map((workerBalance) => (
            <div
              key={workerBalance.worker.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => setSelectedWorker(workerBalance)}
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-800">
                    {workerBalance.worker.name}
                  </h3>
                  {workerBalance.worker.position && (
                    <p className="text-gray-600 text-sm">{workerBalance.worker.position}</p>
                  )}
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteWorker(workerBalance.worker.id);
                  }}
                  className="text-red-500 hover:text-red-700 text-sm"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total dû:</span>
                  <span className="font-semibold text-red-600">
                    {formatCurrency(workerBalance.total_due)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total payé:</span>
                  <span className="font-semibold text-green-600">
                    {formatCurrency(workerBalance.total_paid)}
                  </span>
                </div>
                <hr className="my-2" />
                <div className="flex justify-between">
                  <span className="font-semibold">Solde:</span>
                  <span 
                    className={`font-bold text-lg ${
                      workerBalance.balance > 0 
                        ? 'text-red-600' 
                        : workerBalance.balance < 0 
                        ? 'text-blue-600' 
                        : 'text-gray-600'
                    }`}
                  >
                    {formatCurrency(workerBalance.balance)}
                  </span>
                </div>
              </div>

              <div className="mt-4 text-sm text-gray-500">
                {workerBalance.transactions.length} transaction(s)
              </div>
            </div>
          ))}
        </div>

        {workers.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">Aucun ouvrier enregistré</p>
            <p className="text-gray-400">Commencez par ajouter un ouvrier</p>
          </div>
        )}

        {/* Add Worker Modal */}
        {showAddWorker && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <h2 className="text-xl font-semibold mb-4">Ajouter un nouvel ouvrier</h2>
              <form onSubmit={handleAddWorker}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nom *
                  </label>
                  <input
                    type="text"
                    required
                    value={newWorker.name}
                    onChange={(e) => setNewWorker({...newWorker, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Poste
                  </label>
                  <input
                    type="text"
                    value={newWorker.position}
                    onChange={(e) => setNewWorker({...newWorker, position: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Téléphone
                  </label>
                  <input
                    type="tel"
                    value={newWorker.phone}
                    onChange={(e) => setNewWorker({...newWorker, phone: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="flex gap-4">
                  <button
                    type="submit"
                    className="flex-1 bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors"
                  >
                    Ajouter
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddWorker(false)}
                    className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-md hover:bg-gray-400 transition-colors"
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Add Transaction Modal */}
        {showAddTransaction && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <h2 className="text-xl font-semibold mb-4">Ajouter une transaction</h2>
              <form onSubmit={handleAddTransaction}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ouvrier *
                  </label>
                  <select
                    required
                    value={newTransaction.worker_id}
                    onChange={(e) => setNewTransaction({...newTransaction, worker_id: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Sélectionner un ouvrier</option>
                    {workers.map((wb) => (
                      <option key={wb.worker.id} value={wb.worker.id}>
                        {wb.worker.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Type *
                  </label>
                  <select
                    value={newTransaction.type}
                    onChange={(e) => setNewTransaction({...newTransaction, type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="due">💰 Montant dû</option>
                    <option value="paid">✅ Montant payé</option>
                  </select>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Montant (€) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={newTransaction.amount}
                    onChange={(e) => setNewTransaction({...newTransaction, amount: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <input
                    type="text"
                    value={newTransaction.description}
                    onChange={(e) => setNewTransaction({...newTransaction, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Ex: Salaire semaine 1, Avance..."
                  />
                </div>
                <div className="flex gap-4">
                  <button
                    type="submit"
                    className="flex-1 bg-green-600 text-white py-2 rounded-md hover:bg-green-700 transition-colors"
                  >
                    Ajouter
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddTransaction(false)}
                    className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-md hover:bg-gray-400 transition-colors"
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Worker Details Modal */}
        {selectedWorker && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-semibold">{selectedWorker.worker.name}</h2>
                  {selectedWorker.worker.position && (
                    <p className="text-gray-600">{selectedWorker.worker.position}</p>
                  )}
                  {selectedWorker.worker.phone && (
                    <p className="text-gray-600">📞 {selectedWorker.worker.phone}</p>
                  )}
                </div>
                <button
                  onClick={() => setSelectedWorker(null)}
                  className="text-gray-500 hover:text-gray-700 text-xl"
                >
                  ✕
                </button>
              </div>

              {/* Balance Summary */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-red-50 p-4 rounded-lg text-center">
                  <div className="text-red-600 font-semibold">Total dû</div>
                  <div className="text-xl font-bold text-red-700">
                    {formatCurrency(selectedWorker.total_due)}
                  </div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <div className="text-green-600 font-semibold">Total payé</div>
                  <div className="text-xl font-bold text-green-700">
                    {formatCurrency(selectedWorker.total_paid)}
                  </div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg text-center">
                  <div className="text-gray-600 font-semibold">Solde</div>
                  <div className={`text-xl font-bold ${
                    selectedWorker.balance > 0 
                      ? 'text-red-700' 
                      : selectedWorker.balance < 0 
                      ? 'text-blue-700' 
                      : 'text-gray-700'
                  }`}>
                    {formatCurrency(selectedWorker.balance)}
                  </div>
                </div>
              </div>

              {/* Transactions History */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Historique des transactions</h3>
                {selectedWorker.transactions.length > 0 ? (
                  <div className="space-y-3">
                    {selectedWorker.transactions.map((transaction) => (
                      <div
                        key={transaction.id}
                        className={`p-4 rounded-lg border-l-4 ${
                          transaction.type === 'due' 
                            ? 'bg-red-50 border-red-400' 
                            : 'bg-green-50 border-green-400'
                        }`}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className={`font-semibold ${
                                transaction.type === 'due' ? 'text-red-700' : 'text-green-700'
                              }`}>
                                {transaction.type === 'due' ? '💰 Montant dû' : '✅ Montant payé'}
                              </span>
                              <span className={`text-lg font-bold ${
                                transaction.type === 'due' ? 'text-red-700' : 'text-green-700'
                              }`}>
                                {formatCurrency(transaction.amount)}
                              </span>
                            </div>
                            {transaction.description && (
                              <p className="text-gray-600 mt-1">{transaction.description}</p>
                            )}
                            <p className="text-sm text-gray-500 mt-1">
                              {formatDate(transaction.date)}
                            </p>
                          </div>
                          <button
                            onClick={() => handleDeleteTransaction(transaction.id)}
                            className="text-red-500 hover:text-red-700 ml-4"
                          >
                            🗑️
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">
                    Aucune transaction enregistrée
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;